# LangGraph Review Agent

An automated customer review analysis system that uses LLM technology to detect product/service issues, classify their severity, and track them in a centralized database for resolution.

## Overview

This system processes customer reviews from CSV files, uses local LLM (Ollama) to identify concrete problems and feature requests, classifies their criticality, and logs results to a Notion database for product teams to track and prioritize.

## Features

- **Automated Issue Detection**: Uses LLM to extract actionable problems from customer reviews
- **Smart Classification**: Categorizes issues by type (Crash, Billing, Auth, API, Performance, etc.) and severity (Critical, Major, Minor, Suggestion)
- **Deduplication**: Prevents duplicate issue tracking using content-based hashing
- **Notion Integration**: Automatically logs issues to Notion database for team collaboration
- **Fallback Detection**: Keyword-based detection ensures critical issues aren't missed
- **Feature Request Recognition**: Identifies enhancement requests and feature suggestions

## Architecture

Built using **LangGraph** for workflow orchestration with the following pipeline:

```
CSV Data → Load Reviews → Detect Errors (LLM) → Normalize & Classify → Log to Notion
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd langraph-review-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama** (for local LLM):
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.2  # or your preferred model
   ```

## Configuration

Create a `.env` file in the project root:

```env
# Data source
DATA_PATH=./data/tech_service_reviews_500_with_names_ratings.csv

# LLM Configuration
OLLAMA_MODEL=llama3.2

# Notion Integration
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Optional: Dry run mode (set to "1" to preview without writing to Notion)
NOTION_DRY_RUN=0
```

### Notion Database Setup

Create a Notion database with these properties:
- **ReviewID** (Title)
- **Reviewer** (Rich Text)
- **Date** (Date)
- **ReviewText** (Rich Text)
- **ErrorSummary** (Rich Text)
- **ErrorType** (Multi-select with options: Crash, Billing, Auth, API, Performance, Docs, Permissions, Mobile, UI, Webhooks, Other)
- **Criticality** (Select with options: Critical, Major, Minor, Suggestion, None)
- **Rationale** (Rich Text)
- **Hash** (Rich Text)

## Usage

### Basic Usage

Run the complete pipeline:
```bash
python src/run.py
```

### Testing & Validation

Test individual components:

```bash
# Test first 3 reviews end-to-end
python tests/smoke.py

# Test Ollama connectivity
python tests/ping_ollama.py

# Test Notion connectivity
python tests/notion_ping.py

# Insert demo data to Notion
python tests/notion_logger_demo.py
```

### Dry Run Mode

Preview results without writing to Notion:
```bash
export NOTION_DRY_RUN=1
python src/run.py
```

## Input Data Format

The system expects CSV files with these columns:
- `review_id`: Unique identifier
- `review`: Customer review text
- `username`: Customer username
- `email`: Customer email
- `date`: Review date
- `reviewer_name`: Customer display name
- `rating`: Numeric rating (1-5)

## Issue Classification

### Error Types
- **Crash**: Application crashes, system failures
- **Billing**: Payment issues, billing discrepancies
- **Auth**: Authentication, login problems
- **API**: API timeouts, inconsistencies
- **Performance**: Slow responses, latency issues
- **Docs**: Documentation problems
- **Permissions**: Access control issues
- **Mobile**: Mobile app specific problems
- **UI**: User interface issues
- **Webhooks**: Webhook delivery problems
- **Other**: Feature requests, general issues

### Criticality Levels
- **Critical**: Crashes, data loss, payment failures, outages
- **Major**: Performance issues, billing problems, auth failures
- **Minor**: UI problems, documentation issues, typos
- **Suggestion**: Feature requests, enhancement ideas
- **None**: No actionable issues found

## Project Structure

```
langraph-review-agent/
├── src/
│   ├── run.py                    # Main entry point
│   ├── config.py                 # Configuration management
│   ├── utils.py                  # Data models and utilities
│   ├── graph.py                  # LangGraph workflow definition
│   └── nodes/
│       ├── load_reviews.py       # CSV data loading
│       ├── detect_errors.py      # LLM error detection
│       ├── normalize.py          # Error enrichment
│       ├── classify_criticality.py # Severity classification
│       └── notion_logger.py      # Notion integration
├── tests/                        # Test scripts
├── data/                         # Input CSV files
└── requirements.txt              # Python dependencies
```

## Dependencies

- **langgraph**: Workflow orchestration
- **langchain**: LLM integration framework
- **langchain-community**: Community LLM providers
- **notion-client**: Notion API integration
- **pandas**: Data processing
- **pydantic**: Data validation
- **python-dotenv**: Environment management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   - Ensure Ollama is running: `ollama serve`
   - Verify model is available: `ollama list`

2. **Notion API Error**:
   - Check API key permissions
   - Verify database ID is correct
   - Ensure database has all required properties

3. **CSV Format Error**:
   - Verify all required columns are present
   - Check for proper data types (rating should be numeric)

### Debug Mode

Set environment variable for detailed logging:
```bash
export DEBUG=1
python src/run.py
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review test scripts for examples
3. Open an issue in the repository