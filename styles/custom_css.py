"""
Custom CSS Styles - Thiết kế hiện đại cho ứng dụng
"""


def get_custom_css():
    """Trả về CSS tùy chỉnh cho ứng dụng"""
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }

    .main > div {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }

    /* Header Styles */
    h1 {
        color: #1a202c;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }

    /* Recommendation Card Styles */
    .recommendation-card {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.25);
    }

    .card-rank {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }

    .card-header {
        margin-bottom: 1rem;
    }

    .card-title {
        color: #000000;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }

    .card-body {
        margin-top: 1rem;
    }

    .card-exercise-title {
        color: #000000;
        font-weight: 500;
        font-size: 1.05rem;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background-color: #edf2f7;
        border-radius: 8px;
    }

    .card-info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem 0;
        border-bottom: 1px solid #e2e8f0;
    }

    .card-info-row:last-of-type {
        border-bottom: none;
    }

    .card-label {
        color: #000000;
        font-weight: 500;
        font-size: 0.95rem;
    }

    .card-value {
        color: #000000;
        font-weight: 400;
        text-align: right;
    }

    .difficulty-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .card-score {
        margin-top: 1rem;
        padding: 0.75rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 8px;
        text-align: center;
        color: #000000;
        font-size: 0.95rem;
    }

    .card-score strong {
        color: #667eea;
        font-size: 1.1rem;
    }

    /* AI Explanation Container */
    .ai-explanation-container {
        background: linear-gradient(145deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
    }

    .explanation-text {
        background-color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        color: #000000;
        line-height: 1.5;
        font-size: 0.95rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        max-height: none;
        overflow-y: visible;
        overflow-x: auto;
    }

    .explanation-text * {
        margin-bottom: 0.5rem;
    }

    .explanation-text p {
        margin: 0 0 0.5rem 0;
        word-break: break-word;
    }

    .explanation-text strong,
    .explanation-text b {
        color: #667eea;
        font-weight: 600;
    }

    .explanation-text ul,
    .explanation-text ol {
        margin: 0.5rem 0 0.5rem 1.5rem;
        padding: 0;
    }

    .explanation-text li {
        margin-bottom: 0.3rem;
        word-break: break-word;
    }

    .explanation-text li::marker {
        color: #667eea;
        font-weight: 600;
    }

    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    /* Sidebar text colors - chỉ cho text, không cho inputs */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: white !important;
    }

    /* Labels - màu trắng */
    [data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 500;
    }

    /* Radio button container - background tối để text trắng rõ ràng */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 1rem;
        border-radius: 8px;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }

    /* Select box - text đen trên nền trắng */
    [data-testid="stSidebar"] .stSelectbox > div > div > select {
        background-color: white !important;
        color: #000000 !important;
    }

    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }

    /* Text input - text đen trên nền trắng */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: white !important;
        color: #000000 !important;
    }

    [data-testid="stSidebar"] .stTextInput label {
        color: white !important;
    }

    /* Metrics - text trắng */
    [data-testid="stSidebar"] .stMetric {
        color: white !important;
    }

    [data-testid="stSidebar"] .stMetricValue {
        color: white !important;
    }

    /* Expander - text trắng */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: white !important;
    }

    [data-testid="stSidebar"] .stExpander > button {
        color: white !important;
    }

    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }

    /* Label Styles - Main content area */
    .stTextInput > label,
    .stSelectbox > label,
    .stRadio > label {
        color: #000000 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* Student search bar */
    #student_search_query {
        border-radius: 999px !important;
        border: 2px solid #d9dffb !important;
        padding: 0.65rem 1.25rem !important;
        font-size: 1rem !important;
        background-color: #ffffff !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.12);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }

    #student_search_query:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2) !important;
    }

    /* Student search bar - giống Google Chrome */
    .stTextInput[data-testid="stTextInput"]:has(input[key="student_search_query"]) {
        margin-bottom: 0.5rem;
    }

    .stTextInput[data-testid="stTextInput"]:has(input[key="student_search_query"]) > div > div > input {
        background-color: #f8f9fa !important;
        color: #202124 !important;
        border-radius: 24px !important;
        border: 1px solid #dadce0 !important;
        padding: 10px 16px !important;
        font-size: 16px !important;
        height: 44px !important;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.08);
        transition: all 0.2s ease;
    }

    .stTextInput[data-testid="stTextInput"]:has(input[key="student_search_query"]) > div > div > input:hover {
        background-color: #f8f9fa !important;
        border: 1px solid #d3d3d3 !important;
        box-shadow: 0 1px 8px rgba(32, 33, 36, 0.15);
    }

    .stTextInput[data-testid="stTextInput"]:has(input[key="student_search_query"]) > div > div > input:focus {
        background-color: #ffffff !important;
        border: 1px solid #dadce0 !important;
        box-shadow: 0 1px 6px rgba(32, 33, 36, 0.28);
        outline: none !important;
    }

    .stTextInput[data-testid="stTextInput"]:has(input[key="student_search_query"]) > div > div > input::placeholder {
        color: #5f6368 !important;
        opacity: 1 !important;
    }

    .search-info-bar {
        font-size: 0.85rem;
        color: #5f6368;
        margin: 0.75rem 0 0.5rem 0;
        padding: 0 0.5rem;
        font-weight: 500;
        letter-spacing: 0.2px;
    }

    .search-suggestion-container {
        margin-top: 0.25rem;
        margin-bottom: 1rem;
    }

    .search-suggestion-container [role="radiogroup"] {
        background: #ffffff;
        border: 1px solid #dadce0;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(32, 33, 36, 0.12);
        max-height: 350px;
        overflow-y: auto;
        padding: 0;
    }

    .search-suggestion-container [role="radiogroup"]::-webkit-scrollbar {
        width: 12px;
    }

    .search-suggestion-container [role="radiogroup"]::-webkit-scrollbar-track {
        background: transparent;
    }

    .search-suggestion-container [role="radiogroup"]::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 6px;
        border: 2px solid transparent;
        background-clip: padding-box;
    }

    .search-suggestion-container [role="radiogroup"]::-webkit-scrollbar-thumb:hover {
        background: #bbb;
        background-clip: padding-box;
    }

    .search-suggestion-container [role="radio"] {
        display: flex !important;
        align-items: center;
        gap: 0.5rem;
        padding: 10px 16px !important;
        border-bottom: none !important;
        cursor: pointer;
        transition: background 0.1s ease;
        color: #202124 !important;
    }

    .search-suggestion-container [role="radio"]:hover {
        background: #f1f3f4;
    }

    .search-suggestion-container [role="radio"][aria-checked="true"] {
        background: #e8f0fe;
    }

    .search-suggestion-container [role="radio"] > div:first-child {
        display: none !important;
    }

    .search-suggestion-container [role="radio"] > div {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
    }

    .search-suggestion-container [role="radio"] > div span {
        font-size: 14px;
        font-weight: 400;
        color: #202124;
        word-break: break-word;
    }

    .selected-student-info {
        margin-top: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border-left: none;
        background: linear-gradient(135deg, #e8f0fe 0%, #f0f4ff 100%);
        color: #1a73e8;
        font-weight: 500;
        font-size: 14px;
        box-shadow: 0 1px 4px rgba(32, 33, 36, 0.08);
    }

    /* Input Styles - Main content area */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #000000 !important;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #a0aec0 !important;
        opacity: 0.7;
    }

    .stSelectbox > div > div > select {
        background-color: white !important;
        color: #000000 !important;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
        font-size: 1rem !important;
    }

    .stSelectbox > div > div > select option {
        background-color: white !important;
        color: #000000 !important;
        padding: 10px !important;
    }

    .stRadio > div {
        background-color: rgba(102, 126, 234, 0.05) !important;
        padding: 1rem;
        border-radius: 8px;
    }

    .stRadio label {
        color: #000000 !important;
        font-weight: 500;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        outline: none !important;
    }

    /* Metric Styles */
    [data-testid="stMetricValue"] {
        color: white;
        font-weight: 700;
        font-size: 1.5rem;
    }

    /* Success/Info/Warning Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        font-weight: 500;
    }

    .stSuccess {
        background-color: rgba(76, 175, 80, 0.15) !important;
        border: 2px solid #4CAF50 !important;
        color: #1b5e20 !important;
    }

    .stInfo {
        background-color: rgba(33, 150, 243, 0.15) !important;
        border: 2px solid #2196F3 !important;
        color: #0d47a1 !important;
    }

    .stWarning {
        background-color: rgba(255, 152, 0, 0.15) !important;
        border: 2px solid #FF9800 !important;
        color: #e65100 !important;
    }

    .stError {
        background-color: rgba(244, 67, 54, 0.15) !important;
        border: 2px solid #F44336 !important;
        color: #b71c1c !important;
    }

    /* Expander Styles */
    .streamlit-expanderHeader {
        background-color: #f7fafc;
        border-radius: 8px;
        font-weight: 600;
        color: #2d3748;
    }

    /* DataFrame Styles */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }

    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem;
    }

    .dataframe td {
        padding: 0.75rem;
        border-bottom: 1px solid #e2e8f0;
    }

    /* Radio Button Styles */
    .stRadio > div {
        background-color: #f7fafc;
        padding: 1rem;
        border-radius: 12px;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }

        h1 {
            font-size: 2rem !important;
        }

        .recommendation-card {
            padding: 1rem;
        }

        .card-rank {
            font-size: 1rem;
            padding: 0.4rem 0.8rem;
        }
    }

    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* Scrollbar Styles */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    }
    </style>
    """
