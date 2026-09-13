"""
Evaluation metrics for adaptive alignment
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

class AlignmentEvaluator:
    """Evaluates alignment quality across different metrics"""

    def __init__(self, feature_dim: int, action_dim: int, num_contexts: int):
        self.feature_dim = feature_dim
        self.action_dim = action_dim
        self.num_contexts = num_contexts

    def evaluate_model(self, model: torch.nn.Module, environment,
                      user_ids: List[int], device: torch.device) -> Dict[str, float]:
        """Comprehensive evaluation of a model"""
        model.eval()

        all_metrics = {
            'accuracy': [],
            'alignment_score': [],
            'stability': [],
            'adaptation_accuracy': []
        }

        with torch.no_grad():
            for user_id in user_ids:
                trajectory = environment.generate_interaction_trajectory(user_id)

                states = torch.FloatTensor(np.array(trajectory['states'])).to(device)
                contexts = torch.LongTensor(trajectory['contexts']).to(device)
                timesteps = torch.FloatTensor(trajectory['timesteps']).unsqueeze(1).to(device)
                timesteps_normalized = timesteps / environment.num_timesteps
                human_actions = np.array(trajectory['human_actions'])

                # Get model predictions
                if hasattr(model, 'forward') and 'timestep' in str(model.forward.__code__.co_varnames):
                    logits = model(states, contexts, timesteps_normalized)
                    if isinstance(logits, tuple):
                        logits = logits[0]
                else:
                    logits = model(states, contexts)

                predicted_actions = torch.argmax(logits, dim=1).cpu().numpy()

                # Accuracy
                accuracy = accuracy_score(human_actions, predicted_actions)
                all_metrics['accuracy'].append(accuracy)

                # Alignment score (average prediction confidence on correct actions)
                probs = F.softmax(logits, dim=1)
                correct_probs = probs[range(len(human_actions)), human_actions].cpu().numpy()
                alignment_score = np.mean(correct_probs)
                all_metrics['alignment_score'].append(alignment_score)

                # Stability (variance in predictions over time)
                pred_probs = probs.cpu().numpy()
                temporal_variance = np.mean(np.var(pred_probs, axis=0))
                all_metrics['stability'].append(1.0 - min(temporal_variance, 1.0))

                # Adaptation accuracy (accuracy in second half vs first half)
                mid_point = len(human_actions) // 2
                first_half_acc = accuracy_score(human_actions[:mid_point],
                                               predicted_actions[:mid_point])
                second_half_acc = accuracy_score(human_actions[mid_point:],
                                                predicted_actions[mid_point:])
                adaptation_accuracy = second_half_acc / (first_half_acc + 1e-8)
                all_metrics['adaptation_accuracy'].append(adaptation_accuracy)

        # Aggregate metrics
        results = {
            metric: float(np.mean(values))
            for metric, values in all_metrics.items()
        }

        # Add additional aggregate metrics
        results['user_satisfaction'] = (results['accuracy'] + results['alignment_score']) / 2
        results['agency_preservation'] = results['stability']

        return results

    def evaluate_preference_tracking(self, model: torch.nn.Module, environment,
                                     user_ids: List[int], device: torch.device) -> Dict[str, List[float]]:
        """Evaluate how well the model tracks preference changes over time"""
        model.eval()
        tracking_results = {
            'timesteps': list(range(environment.num_timesteps)),
            'accuracy_over_time': [],
            'alignment_over_time': []
        }

        with torch.no_grad():
            for t in range(environment.num_timesteps):
                t_accuracies = []
                t_alignments = []

                for user_id in user_ids:
                    trajectory = environment.generate_interaction_trajectory(user_id)

                    if t >= len(trajectory['states']):
                        continue

                    state = torch.FloatTensor(trajectory['states'][t]).unsqueeze(0).to(device)
                    context = torch.LongTensor([trajectory['contexts'][t]]).to(device)
                    timestep = torch.FloatTensor([[t / environment.num_timesteps]]).to(device)
                    human_action = trajectory['human_actions'][t]

                    # Get prediction
                    if hasattr(model, 'forward') and 'timestep' in str(model.forward.__code__.co_varnames):
                        logits = model(state, context, timestep)
                        if isinstance(logits, tuple):
                            logits = logits[0]
                    else:
                        logits = model(state, context)

                    pred_action = torch.argmax(logits, dim=1).item()
                    probs = F.softmax(logits, dim=1)
                    alignment = probs[0, human_action].item()

                    t_accuracies.append(1.0 if pred_action == human_action else 0.0)
                    t_alignments.append(alignment)

                tracking_results['accuracy_over_time'].append(np.mean(t_accuracies))
                tracking_results['alignment_over_time'].append(np.mean(t_alignments))

        return tracking_results

    def compare_models(self, results: Dict[str, Dict]) -> Dict[str, any]:
        """Compare multiple models and compute relative improvements"""
        baseline_name = 'static_alignment'
        if baseline_name not in results:
            return {}

        baseline_metrics = results[baseline_name]
        comparisons = {}

        for model_name, metrics in results.items():
            if model_name == baseline_name:
                continue

            improvements = {}
            for metric_name, value in metrics.items():
                if metric_name in baseline_metrics and isinstance(value, (int, float)):
                    baseline_value = baseline_metrics[metric_name]
                    if baseline_value != 0:
                        improvement = ((value - baseline_value) / abs(baseline_value)) * 100
                        improvements[f'{metric_name}_improvement'] = improvement

            comparisons[model_name] = improvements

        return comparisons
