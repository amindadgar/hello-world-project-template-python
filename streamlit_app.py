import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import config
from database import DatabaseManager
from models import TelegramRequestModel

# Configure Streamlit page
st.set_page_config(
    page_title="AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-pending { color: #FF9800; }
    .status-running { color: #2196F3; }
    .status-completed { color: #4CAF50; }
    .status-failed { color: #F44336; }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_requests_data(status_filter: Optional[List[str]] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None,
                      search_text: Optional[str] = None,
                      limit: int = 100,
                      skip: int = 0) -> List[dict]:
    """Load requests data with caching"""
    try:
        db = DatabaseManager()
        requests = db.get_all_requests(
            limit=limit,
            skip=skip,
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to,
            search_text=search_text
        )
        
        # Convert to dict for JSON serialization
        return [request.dict() for request in requests]
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return []

@st.cache_data(ttl=60)
def get_request_counts(status_filter: Optional[List[str]] = None,
                      date_from: Optional[datetime] = None,
                      date_to: Optional[datetime] = None,
                      search_text: Optional[str] = None) -> int:
    """Get total count of requests matching filters"""
    try:
        db = DatabaseManager()
        return db.count_requests(
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to,
            search_text=search_text
        )
    except Exception as e:
        st.error(f"Failed to count requests: {e}")
        return 0

def authenticate():
    """Simple password authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Dashboard Login")
        password = st.text_input("Enter password:", type="password")
        
        if st.button("Login"):
            if password == config.STREAMLIT_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return False
    
    return True

def display_request_detail(request: dict):
    """Display detailed view of a request"""
    st.subheader(f"Request Details: {request['request_id']}")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", request['status'])
    with col2:
        st.metric("User ID", request['user_id'])
    with col3:
        st.metric("Chat ID", request['chat_id'])
    
    # Timestamps
    st.subheader("Timeline")
    timeline_data = []
    
    if request.get('timestamp_received'):
        timeline_data.append({
            'Stage': 'Received',
            'Timestamp': request['timestamp_received'],
            'Status': '✅'
        })
    
    if request.get('timestamp_logged'):
        timeline_data.append({
            'Stage': 'Logged',
            'Timestamp': request['timestamp_logged'],
            'Status': '✅'
        })
    
    if request.get('timestamp_answered'):
        timeline_data.append({
            'Stage': 'Answered',
            'Timestamp': request['timestamp_answered'],
            'Status': '✅'
        })
    
    if timeline_data:
        st.dataframe(pd.DataFrame(timeline_data), use_container_width=True)
    
    # Query and Answer
    st.subheader("Query & Response")
    st.text_area("Query Text", request.get('query_text', ''), disabled=True, height=100)
    st.text_area("Answer Text", request.get('answer_text', 'No answer yet'), disabled=True, height=150)
    
    # Enrichment data
    if request.get('sentiment_score') is not None or request.get('sentiment_label'):
        st.subheader("Sentiment Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sentiment Score", f"{request.get('sentiment_score', 0):.2f}")
        with col2:
            st.metric("Sentiment Label", request.get('sentiment_label', 'N/A'))
    
    # Error information
    if request.get('error_message'):
        st.subheader("Error Information")
        st.error(request['error_message'])
    
    # Technical details
    with st.expander("Technical Details"):
        st.json({
            'request_id': request['request_id'],
            'workflow_instance_id': request.get('workflow_instance_id'),
            'mongodb_id': str(request.get('_id', request.get('id')))
        })

def main_dashboard():
    """Main dashboard interface"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Agent Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_options = ["PENDING", "RUNNING", "COMPLETED", "FAILED"]
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=status_options,
        default=status_options
    )
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    date_range = st.sidebar.date_input(
        "Select date range",
        value=[datetime.now().date() - timedelta(days=7), datetime.now().date()],
        max_value=datetime.now().date()
    )
    
    date_from = None
    date_to = None
    if len(date_range) == 2:
        date_from = datetime.combine(date_range[0], datetime.min.time())
        date_to = datetime.combine(date_range[1], datetime.max.time())
    
    # Search filter
    search_text = st.sidebar.text_input("Search in query/answer text")
    if not search_text.strip():
        search_text = None
    
    # Pagination
    st.sidebar.subheader("Pagination")
    page_size = st.sidebar.selectbox("Items per page", [25, 50, 100, 200], index=2)
    
    # Load and display metrics
    total_count = get_request_counts(selected_statuses, date_from, date_to, search_text)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Get counts by status
    with col1:
        pending_count = get_request_counts(["PENDING"], date_from, date_to, search_text)
        st.metric("Pending", pending_count, help="Requests waiting to be processed")
    
    with col2:
        running_count = get_request_counts(["RUNNING"], date_from, date_to, search_text)
        st.metric("Running", running_count, help="Requests currently being processed")
    
    with col3:
        completed_count = get_request_counts(["COMPLETED"], date_from, date_to, search_text)
        st.metric("Completed", completed_count, help="Successfully processed requests")
    
    with col4:
        failed_count = get_request_counts(["FAILED"], date_from, date_to, search_text)
        st.metric("Failed", failed_count, help="Failed requests")
    
    # Main content area
    st.subheader(f"Request Log ({total_count} total)")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Pagination controls
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    page = st.selectbox("Page", range(1, total_pages + 1), key="page_selector")
    skip = (page - 1) * page_size
    
    # Load requests data
    requests_data = load_requests_data(
        status_filter=selected_statuses,
        date_from=date_from,
        date_to=date_to,
        search_text=search_text,
        limit=page_size,
        skip=skip
    )
    
    if not requests_data:
        st.info("No requests found matching the current filters.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(requests_data)
    
    # Format DataFrame for display
    display_df = df.copy()
    
    # Format timestamps
    timestamp_columns = ['timestamp_received', 'timestamp_logged', 'timestamp_answered']
    for col in timestamp_columns:
        if col in display_df.columns:
            display_df[col] = pd.to_datetime(display_df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Truncate long text fields
    if 'query_text' in display_df.columns:
        display_df['query_text'] = display_df['query_text'].apply(
            lambda x: (x[:50] + '...') if len(str(x)) > 50 else x
        )
    
    if 'answer_text' in display_df.columns:
        display_df['answer_text'] = display_df['answer_text'].apply(
            lambda x: (x[:50] + '...') if len(str(x)) > 50 else x
        )
    
    # Select columns to display
    display_columns = [
        'request_id', 'status', 'user_id', 'chat_id', 'query_text',
        'timestamp_received', 'answer_text', 'sentiment_label'
    ]
    
    # Filter columns that exist in the data
    available_columns = [col for col in display_columns if col in display_df.columns]
    display_df = display_df[available_columns]
    
    # Display table with clickable rows
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'status': st.column_config.TextColumn(
                'Status',
                help='Current status of the request'
            ),
            'request_id': st.column_config.TextColumn(
                'Request ID',
                help='Unique identifier for the request'
            ),
            'timestamp_received': st.column_config.TextColumn(
                'Received',
                help='When the request was received'
            )
        }
    )
    
    # Request detail section
    st.subheader("Request Details")
    request_ids = [req['request_id'] for req in requests_data]
    
    if request_ids:
        selected_request_id = st.selectbox(
            "Select a request to view details:",
            options=request_ids,
            format_func=lambda x: f"{x} ({next(req['status'] for req in requests_data if req['request_id'] == x)})"
        )
        
        if selected_request_id:
            selected_request = next(req for req in requests_data if req['request_id'] == selected_request_id)
            display_request_detail(selected_request)

def main():
    """Main application entry point"""
    
    # Authentication
    if not authenticate():
        return
    
    # Logout button in sidebar
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Main dashboard
    try:
        main_dashboard()
    except Exception as e:
        st.error(f"Dashboard error: {e}")
        st.exception(e)

if __name__ == "__main__":
    main() 