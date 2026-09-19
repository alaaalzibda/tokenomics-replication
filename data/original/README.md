# Tokenomics: Quantifying Where Tokens Are Used in Agentic Software Engineering

Abstract:

LLM-based Multi-Agent (LLM-MA) systems are increasingly applied to automate complex software engineering tasks such as requirements engineering, code generation, and testing. However, their operational efficiency and resource consumption remain poorly understood, hindering practical adoption due to unpredictable costs and environmental impact. To address this, we conduct an analysis of token consumption patterns in an LLM-MA system within the Software Development Life Cycle (SDLC), aiming to understand where tokens are consumed across distinct software engineering activities. We analyze execution traces from 30 software development tasks performed by the ChatDev framework using a GPT-5 reasoning model mapping its internal phases to distinct development stages (Design, Coding, Code Completion, Code Review, Testing, and Documentation) to create a standardized evaluation framework. We then quantify and compare token distribution (input, output, reasoning) across these stages.

Our preliminary findings show that the iterative Code Review stage accounts for the majority of token consumption for an average of 59.4% of tokens. Furthermore, we observe that input tokens consistently constitute the largest share of consumption for an average of 53.9%, providing empirical evidence for potentially significant inefficiencies in agentic collaboration. Our results suggest that the primary cost of agentic software engineering lies not in initial code generation but in automated refinement and verification. Our novel methodology can help practitioners predict expenses and optimize workflows, and it directs future research toward developing more token-efficient agent collaboration protocols.

## Directories

`execution_traces.zip` - The 30 execution traces that were created with ChatDev using GPT-5 Reasoning LLM.

`scripts_and_data.zip` includes the following directories:

-   **data**
    -   **processed_data** (directory containing pie charts, bar charts, and tables with descriptive statistics)
    -   **ChatDev_GPT-5_Trace_Analysis_Results.json** (json file containing all extracted data from the 30 execution traces)
-   **scripts** (directory containing scripts used in the project)
    -   **token_usage_extractor_chatdev_gpt_5.py** (token usage data extraction from all 30 execution traces)
    -   **token_usage_breakdown_charts.py** (creates pie charts, an average bar chart, and a table containing descriptive statistics for phase-by-phase token usage breakdown for all 30 execution traces)
    -   **token_input_vs_output_charts.py** (creates bar charts showing the distribution of input, output, and reasoning tokens for all 30 execution traces)
    -   **token_input_output_ratio_table.py** (creates tables showing descriptive statistics for input, output, and reasoning tokens for all 30 execution traces)
-   **README.md** (the file you are currently reading)

## Getting Started

1. **Unzip** `scripts_and_data.zip`.

2. **Install the required Python libraries.**  
   It is recommended to use a virtual environment.  
   You can create a `requirements.txt` file with the following content:

    ```text
    pandas
    numpy
    scipy
    matplotlib
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Data Preparation and Analysis

The analysis is a two-step process:

1. **Extract the token data** from the raw execution traces.
2. **Run the analysis scripts** to generate charts and tables.

---

### Step 1: Data Extraction

This step uses `token_usage_extractor_chatdev_gpt_5.py` to parse all `.log` files.

1. **Unzip** `execution_traces.zip`.  
   This will create a folder (e.g., `ChatDev_GPT-5`) containing 30 sub-directories, each with a `.log` file.

2. **Open** `scripts/token_usage_extractor_chatdev_gpt_5.py`.

3. In the `if __name__ == "__main__":` block at the bottom,  
   change the `traces_folder_path` variable to point to the location where you unzipped the traces, for example:

    ```python
    traces_folder_path = ".../ChatDev_GPT-5"
    ```

4. **Run the script:**

    ```bash
    python scripts/token_usage_extractor_chatdev_gpt_5.py
    ```

    **Input:**  
    The folder containing the 30 execution traces.

    **Output:**  
    The script will create `ChatDev_GPT-5_Trace_Analysis_Results.json` and save it inside the `scripts/` directory.

---

### Step 2: Analysis and Chart/Table Generation

All analysis scripts read the `ChatDev_GPT-5_Trace_Analysis_Results.json` file.  
You must edit the `json_file_path` variable at the bottom of each script to point to:

```
scripts/ChatDev_GPT-5_Trace_Analysis_Results.json
```

---

#### `token_usage_breakdown_charts.py`

Generates charts for the percentage of token usage by phase  
(e.g., what percentage of tokens was spent in "Code Review").

**Input:**  
`scripts/ChatDev_GPT-5_Trace_Analysis_Results.json`

**Output:**  
Creates a new directory (by default, `scripts/token_distribution_charts/`):

-   A pie chart for each project (e.g., `Project_Name_token_distribution.png`).
-   An aggregate average bar chart (`AVERAGE_token_distribution_BAR.png`) showing the mean token usage per phase across all projects.
-   A descriptive statistics table (`descriptive_statistics_table.txt`) with stats for phase percentages.

---

#### `token_input_vs_output_charts.py`

Generates bar charts showing the absolute token breakdown (Input vs. Output vs. Reasoning) for each phase.

**Input:**  
`scripts/ChatDev_GPT-5_Trace_Analysis_Results.json`

**Output:**  
Creates a new directory (by default, `scripts/token_input_vs_output_bar_charts/`):

-   A detailed bar chart for each project (e.g., `Project_Name_token_distribution_bars.png`) comparing the raw counts of Input, Output, and Reasoning tokens for each phase.
-   Prints a summary of **"non-input-dominated"** phases to the console.

---

#### `token_input_output_ratio_table.py`

Generates text-based tables and descriptive statistics for the ratios of Input, Output, and Reasoning tokens.

**Input:**  
`scripts/ChatDev_GPT-5_Trace_Analysis_Results.json`

**Output:**  
Creates several `.txt` files in the directory specified by `output_dir`:

-   `token_ratios_table.txt`: A table of I:O:R tokens and percentages for each individual trace.
-   `token_ratios_summary.txt`: Summary statistics (Mean, Median, SD, etc.) for the Input, Output, and Reasoning percentages across all traces.
-   `phase_token_ratios_breakdown.txt`: A detailed statistical breakdown (Mean, SD, Median, Min, Max) of token ratios for each mapped SDLC phase (e.g., Design, Code Review).
