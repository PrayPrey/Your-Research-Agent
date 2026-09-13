import seaborn as sns
import matplotlib
import matplotlib.pylab as plt
from matplotlib.colors import LinearSegmentedColormap
import os

import pandas as pd
import numpy as np

from experiments.babilong.metrics import compare_answers, TASK_LABELS


def get_accuracy(tasks, lengths, results_folder, model_name, prompt_name):
    accuracy = np.zeros((len(tasks), len(lengths)))
    for j, task in enumerate(tasks):
        for i, ctx_length in enumerate(lengths):
            if results_folder.startswith('/home'):
                fname = f'{results_folder}/{model_name}/{task}_{ctx_length}_{prompt_name}.csv'
            else:
                fname = f'./{results_folder}/{model_name}/{task}_{ctx_length}_{prompt_name}.csv'
            if not os.path.isfile(fname):
                print(f'No such file: {fname}')
                continue

            df = pd.read_csv(fname)

            if df['output'].dtype != object:
                df['output'] = df['output'].astype(str)
            df['output'] = df['output'].fillna('')


            df['correct'] = df.apply(lambda row: compare_answers(row['target'], row['output'],
                                                                row['question'], TASK_LABELS[task]
                                                                ), axis=1)
            score = df['correct'].sum()
            accuracy[j, i] = 100 * score / len(df) if len(df) > 0 else 0
    return accuracy

if __name__ == "__main__":
    results_folder = './experiments/babilong'
    # model_name = "meta-llama/Llama-3.2-1B-Instruct"
    model_name = 'distill_llama3_2_1b_wsw64_fd32_instruct'
    # prompt_name = 'instruction_yes_examples_yes_post_prompt_yes_chat_template_no_system_prompt_no'
    # prompt_name = 'instruction_no_examples_no_post_prompt_no_chat_template_no_system_prompt_no'
    prompt_name = 'instruction_yes_examples_yes_post_prompt_yes_chat_template_yes_system_prompt_yes'

    # tasks = ['qa1', 'qa2', 'qa3', 'qa4', 'qa5']#, 'qa6', 'qa7', 'qa8', 'qa9', 'qa10']
    # lengths = ['0k', '1k', '2k', '4k', '8k', '16k', '32k']
    # tasks = ['qa1', 'qa2', 'qa3', 'qa4', 'qa5']
    tasks = ['qa1', 'qa2', 'qa3']
    lengths = ['0k', '1k', '2k', '4k', '8k', '16k', '32k']
    accuracy = np.zeros((len(tasks), len(lengths)))
    accuracy = get_accuracy(tasks, lengths, results_folder, model_name, prompt_name)

    # Set large font sizes for better visibility in the PDF
    matplotlib.rc('font', size=14)

    # Create a colormap for the heatmap
    cmap = LinearSegmentedColormap.from_list('ryg', ["red", "yellow", "green"], N=256)

    # Create the heatmap

    fig, ax = plt.subplots(figsize=(5, 2))  # Adjust the size as necessary (5,3.5)
    sns.heatmap(accuracy, cmap=cmap, vmin=0, vmax=100, annot=True, fmt=".0f",
                linewidths=.5, xticklabels=lengths, yticklabels=tasks, ax=ax, cbar_kws={"orientation": "horizontal"})
    ax.set_title(f'Performance of {model_name} \n on BABILong \n')
    # plt.subplots_adjust(bottom=-0.9)
    ax.set_xlabel('Context size')
    ax.set_ylabel('Tasks')

    # Save the figure to a PDF
    pdf_name = f'./{results_folder}/{model_name}/a_res.png'
    plt.savefig(pdf_name, bbox_inches='tight', dpi=300)
    plt.show()