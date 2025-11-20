# Project Database - Progress Report
**Date:** November 20, 2025

## Summary
Conducted comprehensive quality evaluation of AI-generated READMEs using three qwen2.5-coder model variants (7b, 14b, 32b). Evaluated 15 generated READMEs across 5 projects, measuring accuracy, completeness, and clarity. Findings show 32b model produces best quality but all models require manual review for production use.

## Accomplishments

### 1. Model Comparison Notebook Setup
**Created comprehensive Jupyter notebook for README quality testing:**

- **Project selection** - Query database for projects without READMEs but with code
- **Random sampling** - Select 5 projects with seed=42 for reproducibility
- **Multi-model generation** - Generate READMEs using 3 model sizes:
  - qwen2.5-coder:7b (fast, ~10-15s per README)
  - qwen2.5-coder:14b (balanced, ~20-30s per README)
  - qwen2.5-coder:32b (best quality, ~40-60s per README)
- **Timing capture** - Measure generation time for each README
- **Result storage** - Save READMEs to markdown files and timing data to CSV

**Location:** `notebooks/spikes/model_comparison.ipynb`

### 2. Generated READMEs for Test Projects
**Successfully generated 15 READMEs for 5 diverse projects:**

1. **mujoco-experiments** - MuJoCo physics simulation with robot arm
2. **fast_index** - Cython-optimized index finder for sorted lists
3. **ii-microservice** - Financial holdings management system
4. **market-research** - GitHub repository data scraper
5. **eutopia** - Empty project (edge case test)

**Output:** `notebooks/output/model_comparison/` (15 markdown files + timing CSV)

### 3. Comprehensive Quality Evaluation
**Evaluated each README on three dimensions (1-5 scale):**

- **Accuracy** - Does it correctly describe what the project does?
- **Completeness** - Does it cover important aspects?
- **Clarity** - Is it well-written and easy to understand?

**Methodology:**
1. Examined actual project code to understand ground truth
2. Read all 3 generated READMEs per project
3. Scored each README objectively
4. Documented justifications for each score

### 4. Key Findings

#### Model Performance Rankings

**32b Model - Best Overall**
- Accuracy: 4.2/5 average
- Completeness: 4.0/5 average
- Clarity: 4.6/5 average
- Most context-aware, best structure
- Generation time: 40-60 seconds

**14b Model - Balanced**
- Accuracy: 4.0/5 average
- Completeness: 3.4/5 average
- Clarity: 4.0/5 average
- Good technical accuracy
- Generation time: 20-30 seconds

**7b Model - Fast**
- Accuracy: 3.6/5 average
- Completeness: 3.4/5 average
- Clarity: 3.8/5 average
- Adequate for simple projects
- Generation time: 10-15 seconds

#### Project-Specific Results

**Excellent (4-5/5):**
- eutopia: 5/5 (all models correctly identified empty project)
- ii-microservice: 4-5/5 (all models understood financial holdings management)
- mujoco-experiments: 4-5/5 (all models grasped physics simulation)

**Poor (2-3/5):**
- market-research: 2-3/5 (all models misunderstood GitHub API usage, thought it parsed text files)
- fast_index: 3-4/5 (7b incorrectly claimed binary search, wrong import paths)

#### Common Issues Across All Models

1. **Algorithm misidentification** - Models guess implementation details without verifying
2. **Import path errors** - Usage examples often have wrong module names
3. **API confusion** - Mistook GitHub API calls for file parsing
4. **Missing unique features** - Generic descriptions overlook special functionality
5. **Non-working examples** - Code samples reference undefined variables

### 5. Documentation Created

**Evaluation Results:**
- `readme_evaluation.csv` - Detailed scores and notes for all 15 READMEs
- `evaluation_summary.md` - Comprehensive analysis with recommendations
- `timing_results.csv` - Generation time and statistics

**CLAUDE.md Update:**
- Added section on Jupyter notebook editing best practices
- Documented cell ordering issues with NotebookEdit tool
- Reminder to verify cell order after edits

## Technical Highlights

### Notebook Development Challenges
- **Cell ordering issue** - NotebookEdit with `insert` mode adds cells in reverse order
- **Solution** - Rewrite entire notebook using Write tool when order is wrong
- **Prevention** - Added reminder to CLAUDE.md to always verify after edits

### Evaluation Methodology
- **Ground truth verification** - Examined actual project code before evaluation
- **Objective scoring** - Used 1-5 scale with documented justifications
- **Comprehensive coverage** - All 15 READMEs evaluated against actual implementations

### Data Collection
- **Timing data** - Captured generation time for performance comparison
- **Structured output** - CSV format for easy analysis
- **Multiple formats** - Both detailed markdown and summary statistics

## Recommendations

### Model Selection Guidelines

**Use 32b when:**
- README quality is critical
- Project is customer-facing
- Need well-structured, clear documentation
- Generation time (extra 30-60s) is acceptable

**Use 14b when:**
- Balancing quality and speed
- Need good technical accuracy
- Working with projects with unique features

**Use 7b when:**
- Speed is priority
- Generating drafts for simple projects
- Planning to manually review and edit
- Cost/resource constraints

### Improvement Opportunities

1. **Better code analysis** - More thorough AST parsing could improve accuracy
2. **Dependency validation** - Check actual imports vs. claimed dependencies
3. **Test execution** - Run tests to understand actual behavior
4. **Example validation** - Verify usage examples against actual API
5. **RAG improvements** - Better chunk selection for relevant code sections

### Production Usage Guidelines

**Manual review is essential for:**
- Technical accuracy of implementation details
- Verification of dependencies and installation instructions
- Testing of usage examples
- Checking import paths and module names

**All models struggle with:**
- Complex projects with external API integrations
- Accurate algorithm descriptions
- Correct usage examples with actual APIs

## Statistics

- **Projects evaluated:** 5
- **READMEs generated:** 15
- **Models tested:** 3 (7b, 14b, 32b)
- **Evaluation dimensions:** 3 (accuracy, completeness, clarity)
- **Total generation time:** ~5 minutes (all 15 READMEs)
- **Output files:** 18 (15 READMEs + 3 data files)

## Files Created/Modified

**New files:**
- `notebooks/spikes/model_comparison.ipynb` - Model comparison notebook
- `notebooks/output/model_comparison/*.md` - 15 generated READMEs
- `notebooks/output/model_comparison/timing_results.csv` - Generation timing data
- `notebooks/output/model_comparison/readme_evaluation.csv` - Quality scores
- `notebooks/output/model_comparison/evaluation_summary.md` - Analysis and recommendations

**Modified files:**
- `CLAUDE.md` - Added Jupyter notebook editing guidelines

## Next Steps

### Immediate Actions
1. **Review findings** - Discuss which model to use for batch processing
2. **Decide on quality threshold** - Determine acceptable accuracy level
3. **Plan batch processing** - Ready to process remaining 162 projects

### Future Enhancements
1. **Improve RAG pipeline** - Address accuracy issues identified
2. **Validate examples** - Add step to test usage examples
3. **Dependency checking** - Verify imports against actual code
4. **Custom prompts** - Tune prompts based on project type
5. **Multi-pass generation** - Generate, review, refine cycle

### Batch Processing Considerations
- **Model choice** - 32b recommended for quality, but 3x slower than 7b
- **Error handling** - Implement retry logic for failed generations
- **Progress tracking** - Add checkpoint/resume capability
- **Quality monitoring** - Sample random outputs for ongoing evaluation

## Lessons Learned

### What Worked Excellently
1. **Systematic evaluation** - Comparing models side-by-side revealed clear differences
2. **Diverse test set** - 5 projects of varying complexity showed model strengths/weaknesses
3. **Objective scoring** - 1-5 scale with justifications provided clear rankings
4. **Ground truth comparison** - Examining actual code was essential for accurate evaluation

### Technical Insights
- **Larger models = better quality** - Clear improvement from 7b → 14b → 32b
- **All models need review** - Even 32b makes factual errors on complex projects
- **Empty projects handled well** - All models correctly identified no-code situation
- **API understanding weak** - All models struggled with external API projects

### Process Improvements
- **Notebook cell ordering** - Need to use Write tool, not NotebookEdit for complex notebooks
- **Timing capture important** - Helps make speed/quality trade-off decisions
- **CSV output valuable** - Easy to analyze and share results

## Conclusion

Successfully completed comprehensive quality evaluation of three qwen2.5-coder model variants for README generation. Results show clear quality improvement with model size (32b > 14b > 7b), but all models require manual review for production use. Key weaknesses identified: algorithm misidentification, wrong import paths, and API confusion. System is ready for batch processing of 162 remaining projects, with 32b model recommended for best quality despite slower generation time.

**Status:** ✅ Evaluation complete, recommendations documented, ready for decision on batch processing approach

---

*Report generated after model comparison and evaluation session*
*All findings documented with objective scoring and recommendations* 📊
