# Legal AI Assistant

An intelligent legal assistant that helps users analyze legal documents, answer legal questions, compare contracts, perform risk assessments, and generate customized legal documents.

## Features

- **Document Analysis**: Upload and analyze legal documents to extract key information, clauses, and insights.

- **Legal Queries**: Ask legal questions and get AI-powered responses with citations to relevant legal sources.

- **Contract Comparison**: Compare two legal documents side-by-side to identify differences and understand their legal implications.

- **Legal Risk Assessment**: Upload a contract to receive a comprehensive risk evaluation with risk scores by category and specific recommendations for improvement.

- **Contract Generator**: Create customized legal contracts by answering simple questions. Generate NDAs, employment agreements, consulting contracts, and more.

## Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI/ML**: Google Gemini API
- **Document Processing**: PyPDF2, docx2txt

## Setup and Installation

### Prerequisites

- Python 3.9+
- pip

### Installation Steps

1. Clone the repository:
```
git clone https://github.com/yourusername/legal-ai.git
cd legal-ai
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the backend server:
```
cd backend
uvicorn app.main:app --reload
```

5. Run the Streamlit frontend in a new terminal:
```
cd streamlit_app
streamlit run app.py
```

## Usage

1. Open your browser and navigate to `http://localhost:8501` to access the Streamlit frontend.
2. Select the desired feature from the sidebar.
3. Follow the on-screen instructions for the selected feature.

## Testing

Run the test suite to verify that the application is working correctly:
```
pytest test_app.py
```

## Development

### Project Structure

```
legal-ai/
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Main application
│   │   ├── models/         # Data models
│   │   └── routers/        # API routes
│   └── tests/              # Backend tests
│
├── streamlit_app/          # Streamlit frontend
│   └── app.py              # Main Streamlit application
│
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only and does not constitute legal advice. Please consult with a licensed attorney for professional legal assistance.
