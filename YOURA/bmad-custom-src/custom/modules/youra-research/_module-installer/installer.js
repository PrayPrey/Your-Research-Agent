// YouRA Adaptive Research Pipeline Module Installer
// Custom installation logic for MCP server verification and Archon setup

/**
 * @param {Object} options - Installation options
 * @param {string} options.projectRoot - Project root directory
 * @param {Object} options.config - Module configuration from install-config.yaml
 * @param {Array} options.installedIDEs - List of IDE codes being configured
 * @param {Object} options.logger - Logger instance (log, warn, error methods)
 * @returns {boolean} - true if successful, false to abort installation
 */
async function install(options) {
  const { projectRoot, config = {}, logger } = options;

  logger.log('');
  logger.log('🚀 YouRA Adaptive Research Pipeline');
  logger.log('   Deep Learning research automation pipeline');
  logger.log('');

  // Default output path (alpha.22 compatibility)
  const researchOutputPath = config.research_output_path || 'docs/youra_research';

  // 1. MCP server guidance
  logger.log('📡 MCP servers used by YouRA:');
  logger.log('');
  logger.log('  [Required]');
  logger.log('    • Archon      - Task management & Knowledge Base');
  logger.log('    • Serena      - Code analysis & symbolic editing');
  logger.log('');
  logger.log('  [For Phase 1 research]');
  logger.log('    • Semantic Scholar - Academic paper search');
  logger.log('    • Exa              - GitHub/web search');
  logger.log('');
  logger.log('  [For Phase 2 reasoning]');
  logger.log('    • ClearThought     - Structured reasoning tools');
  logger.log('');

  // 2. Create research output directory
  const fs = require('fs');
  const path = require('path');

  const outputPath = path.join(projectRoot, researchOutputPath);

  if (!fs.existsSync(outputPath)) {
    try {
      fs.mkdirSync(outputPath, { recursive: true });
      logger.log(`📁 Created research output directory: ${outputPath}`);
    } catch (error) {
      logger.error(`❌ Failed to create output directory: ${error.message}`);
      return false;
    }
  } else {
    logger.log(`📁 Research output directory verified: ${outputPath}`);
  }

  // 3. Installation completion and usage guidance
  logger.log('');
  logger.log('🎉 YouRA Adaptive Research Pipeline installation complete!');
  logger.log('');
  logger.log('═══════════════════════════════════════════════════════════════');
  logger.log('');
  logger.log('📌 Pipeline structure:');
  logger.log('   Phase 0 → 1 → 2A → 2A-Ext → 2B → (2C → 3 → 4) × N → 5 → 6 → 6.5');
  logger.log('');
  logger.log('📌 Primary skill commands:');
  logger.log('');
  logger.log('  [Full pipeline]');
  logger.log('    /full-pipeline-unattended   Unattended full run');
  logger.log('');
  logger.log('  [Individual phases]');
  logger.log('    /phase0-brainstorm          Research question discovery');
  logger.log('    /phase1-targeted            Targeted research collection');
  logger.log('    /phase2a-dialogue           Two-agent hypothesis discussion');
  logger.log('    /phase2a-extended           Scientific hypothesis clarification');
  logger.log('    /phase2b-planning           Validation roadmap generation');
  logger.log('');
  logger.log('  [Hypothesis loop]');
  logger.log('    /hypothesis-loop            Automated hypothesis verification loop');
  logger.log('');
  logger.log('  [Paper writing]');
  logger.log('    /phase6-paper-writing       Generate ICML-format paper');
  logger.log('    /phase65-adversarial-review Multi-round review');
  logger.log('');
  logger.log('═══════════════════════════════════════════════════════════════');
  logger.log('');
  logger.log(`📁 Research output path: ${outputPath}`);
  logger.log('');

  return true;
}

module.exports = { install };
