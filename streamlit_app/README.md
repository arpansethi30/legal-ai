# LexCounsel AI Streamlit App

This Streamlit app provides a user-friendly interface to LexCounsel AI's powerful legal reasoning and analysis capabilities.

## Features

- **Legal Reasoning**: Analyze legal text using multiple methodologies
- **Expert Consultation**: Get insights from simulated legal experts
- **Legal Issue Identification**: Automatically identify potential legal issues
- **Client Memo Generation**: Create professional client memos
- **Authority Search**: Find and analyze with legal authorities
- **Task Management**: Generate task lists and time entries

## Setup

### Prerequisites

- Python 3.9+
- Backend API running (LexCounsel AI backend)

### Installation

1. Clone the repository (if you haven't already)
2. Navigate to the streamlit_app directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the streamlit_app directory with the following variables:

```
API_BASE_URL=http://localhost:8000
```

Adjust the URL if your backend is running on a different host or port.

## Running the App

From the streamlit_app directory, run:

```bash
streamlit run app.py
```

The app will be available at http://localhost:8501

## Backend Requirements

Make sure the LexCounsel AI backend is running before using the app. Start it with:

```bash
cd ../backend
python -m app.main
```

## Document Processing

The app supports uploading and processing:

- PDF files
- Word documents (.docx)
- Text files (.txt)

## Troubleshooting

- If you see connection errors, make sure the backend is running
- Check the API_BASE_URL in your .env file
- For issues with file uploads, check file permissions and format compatibility 