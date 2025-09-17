# FlexOn AI-Powered Query Dashboard Setup

## Overview
The FlexOn dashboard has been enhanced with Google Gemini AI integration for intelligent natural language to Django ORM conversion.

## Features
- **AI-Powered Query Processing**: Uses Google Gemini Pro to convert natural language queries into Django ORM
- **Smart Database Schema Understanding**: AI has comprehensive knowledge of your database models
- **Fallback System**: If Gemini AI is unavailable, falls back to pattern-based query generation
- **Enhanced UI**: Modern, responsive interface with better UX
- **Real-time Processing**: Instant query processing with loading indicators

## Setup Instructions

### 1. Install Dependencies
```bash
pip install google-generativeai
```

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy your API key

### 3. Configure Environment
Set your Gemini API key as an environment variable:

**Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY=your_api_key_here
```

**Or create a .env file:**
```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Access FlexOn Dashboard
Navigate to: `http://localhost:8000/flexon/`

## Usage Examples

### Natural Language Queries
- "Show me top 10 students with highest LeetCode problems"
- "Find all students with Python projects"
- "List students with cloud computing certifications"
- "Show placement statistics by department"
- "Students with more than 2 projects and LeetCode score > 100"

### Advanced Queries
- "Find CSE students with AWS certifications who have completed more than 5 LeetCode problems"
- "Show me students with both machine learning projects and data science certifications"
- "List all unplaced students with high LeetCode scores"

## Technical Details

### AI Schema Context
The Gemini AI has been trained with comprehensive information about:
- Student model (roll_no, name, dept, year, etc.)
- Projects model with technology relationships
- Certificate model with providers and categories  
- LeetCode performance data
- Placement and offer information
- Faculty and coordination data

### Security
- Only read-only ORM queries are generated
- No create, update, or delete operations allowed
- Input sanitization and validation
- Safe evaluation environment

### Fallback System
If Gemini AI is unavailable:
- Automatic fallback to pattern-based matching
- Basic query patterns still supported
- Graceful error handling

## Troubleshooting

### Common Issues
1. **"Gemini AI error"**: Check your API key and internet connection
2. **"Invalid ORM query"**: The AI couldn't generate valid Django ORM for your query
3. **No results**: Try rephrasing your query or use quick action buttons

### Error Messages
- Check Django logs for detailed error information
- AI processing errors are logged with full traceback
- Fallback system activates automatically on AI failures

## Changelog
- **v2.0**: Added Google Gemini AI integration
- **v2.0**: Removed legacy query builder
- **v2.0**: Enhanced UI with modern design
- **v2.0**: Added intelligent query processing
- **v2.0**: Improved error handling and fallback system