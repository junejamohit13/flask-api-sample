#components/DataTable.tsx
import React, { useEffect, useState } from 'react';
import { DataGrid, GridColDef, GridCellEditStopParams, GridRenderEditCellParams } from '@mui/x-data-grid';
import { useQuery, useMutation } from '@apollo/client';
import { GET_USER_TABLES_DATA, UPDATE_DATA, UPDATE_COMMENT } from '../graphql/queries';
import { TableData, UpdateDataInput } from '../types';
import { debounce } from 'lodash';
import { TextField } from '@mui/material';

interface DataTableProps {
    username: string;
}

interface ColumnComment {
    value: string;
}

interface ColumnComments {
    [key: string]: ColumnComment;  // question -> {value: string} mapping
}

interface TableComments {
    [column: string]: ColumnComments;  // column -> comments mapping
}

interface ProcessedRow {
    id: string;
    tableName: string;
    primaryKey: string;
    column: string;
    value: string;
    q1: string;
    q2: string;
    q3: string;
    q4: string;
    [key: string]: string; // Add index signature
}

// Create a new EditCell component
const EditCell = React.memo((params: GridRenderEditCellParams) => {
    const [value, setValue] = useState(params.value || '');

    return (
        <TextField
            fullWidth
            multiline
            rows={4}
            value={value}
            onChange={(e) => {
                const newValue = e.target.value;
                setValue(newValue);
                params.api.setEditCellValue({ 
                    id: params.id, 
                    field: params.field, 
                    value: newValue
                });
            }}
            onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.stopPropagation();
                }
            }}
            onFocus={(e) => {
                e.target.select();
            }}
            sx={{ backgroundColor: 'white' }}
        />
    );
});

export const DataTable: React.FC<DataTableProps> = ({ username }) => {
    const [rows, setRows] = useState<ProcessedRow[]>([]);
    const [columns, setColumns] = useState<GridColDef[]>([]);

    // Query to fetch data
    const { data, loading, error } = useQuery(GET_USER_TABLES_DATA, {
        variables: { username }
    });

    // Mutation for updating data
    const [updateData] = useMutation(UPDATE_DATA);

    // Add comment mutation
    const [updateComment] = useMutation(UPDATE_COMMENT);

    // Debounced update function
    const debouncedUpdate = debounce((params: UpdateDataInput) => {
        updateData({
            variables: {
                input: params
            }
        });
    }, 500);

    // Debounced update for comments
    const debouncedUpdateComment = debounce((params: {
        username: string;
        tableName: string;
        primaryKey: string;
        columnName: string;
        question: string;
        answer: string;
    }) => {
        updateComment({
            variables: {
                input: params
            }
        });
    }, 500);

    const processRowUpdate = React.useCallback(
        (newRow: ProcessedRow, oldRow: ProcessedRow) => {
            const field = Object.keys(newRow).find(key => newRow[key] !== oldRow[key]);
            if (!field) return oldRow;

            if (field === 'value') {
                const updateParams: UpdateDataInput = {
                    username: username,
                    tableName: newRow.tableName,
                    primaryKey: newRow.primaryKey,
                    columnName: newRow.column,
                    value: newRow.value
                };
                debouncedUpdate(updateParams);
            } 
            else if (field.startsWith('q')) {
                const commentParams = {
                    username: username,
                    tableName: newRow.tableName,
                    primaryKey: newRow.primaryKey,
                    columnName: newRow.column,
                    question: field,
                    answer: newRow[field]
                };
                console.log('Building comment params:', {
                    field,
                    newValue: newRow[field],
                    finalParams: commentParams
                });
                debouncedUpdateComment(commentParams);
            }

            return newRow;
        },
        [username, debouncedUpdate, debouncedUpdateComment]
    );

    // Process data when it arrives
    useEffect(() => {
        if (data?.getUserTablesData) {
            console.log('Raw GraphQL data:', data.getUserTablesData);

            const processedRows: ProcessedRow[] = [];
            
            data.getUserTablesData.forEach((item: TableData) => {
                Object.entries(item.data || {}).forEach(([column, value]) => {
                    const columnComments = item.comments?.[column] || {};
                    console.log('Processing comments for column:', column, columnComments);
                    
                    processedRows.push({
                        id: `${item.tableName}-${item.primaryKey}-${column}`,
                        tableName: item.tableName,
                        primaryKey: item.primaryKey,
                        column,
                        value: value?.toString() ?? '',
                        // Direct access to comment values since we simplified the structure
                        q1: columnComments['q1'] ?? '',
                        q2: columnComments['q2'] ?? '',
                        q3: columnComments['q3'] ?? '',
                        q4: columnComments['q4'] ?? ''
                    });
                });
            });

            console.log('Processed rows:', processedRows);

            const columns: GridColDef[] = [
                { field: 'tableName', headerName: 'Table', width: 150 },
                { field: 'primaryKey', headerName: 'Primary Key', width: 150 },
                { field: 'column', headerName: 'Column', width: 150 },
                { field: 'value', headerName: 'Value', width: 150, editable: true },
                { 
                    field: 'q1', 
                    headerName: 'Question 1', 
                    width: 200, 
                    editable: true,
                    renderEditCell: (params) => <EditCell {...params} />
                },
                { 
                    field: 'q2', 
                    headerName: 'Question 2', 
                    width: 200, 
                    editable: true,
                    renderEditCell: (params) => <EditCell {...params} />
                },
                { 
                    field: 'q3', 
                    headerName: 'Question 3', 
                    width: 200, 
                    editable: true,
                    renderEditCell: (params) => <EditCell {...params} />
                },
                { 
                    field: 'q4', 
                    headerName: 'Question 4', 
                    width: 200, 
                    editable: true,
                    renderEditCell: (params) => <EditCell {...params} />
                }
            ];

            setRows(processedRows);
            setColumns(columns);
        }
    }, [data]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <div style={{ height: 400, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                processRowUpdate={processRowUpdate}
                disableRowSelectionOnClick
            />
        </div>
    );
}; 

//components/Layout.tsx

import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <>
            <AppBar position="static">
                <Toolbar>
                    <Typography variant="h6" style={{ flexGrow: 1 }}>
                        Data Review App
                    </Typography>
                    <Button color="inherit" component={RouterLink} to="/">
                        Home
                    </Button>
                    <Button color="inherit" component={RouterLink} to="/review">
                        Review
                    </Button>
                </Toolbar>
            </AppBar>
            <Container style={{ marginTop: 20 }}>
                {children}
            </Container>
        </>
    );
};

export default Layout; 

#components/QueueReviewTable.tsx
import React from 'react';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery, useMutation } from '@apollo/client';
import { GET_REVIEW_QUEUE, UPDATE_COMMENT_REVIEW, MARK_REVIEW_AS_COMMITTED } from '../graphql/queries';
import { TextField, Button } from '@mui/material';

const ReviewQueueTable: React.FC = () => {
    const { data, loading, error, refetch } = useQuery(GET_REVIEW_QUEUE);
    const [updateCommentReview] = useMutation(UPDATE_COMMENT_REVIEW);
    const [markAsCommitted] = useMutation(MARK_REVIEW_AS_COMMITTED);

    const handleCommentChange = async (id: number, question: string, value: string) => {
        try {
            await updateCommentReview({
                variables: {
                    input: {
                        id,
                        question,
                        answer: value
                    }
                }
            });
        } catch (error) {
            console.error('Error updating review comment:', error);
            alert('Error updating review comment');
        }
    };

    const handleCommit = async (id: number) => {
        try {
            await markAsCommitted({
                variables: { id }
            });
            alert('Successfully committed review');
            refetch(); // Refresh the table
        } catch (error) {
            console.error('Error marking as committed:', error);
            alert('Error marking as committed');
        }
    };

    const columns: GridColDef[] = [
        { field: 'userName', headerName: 'User', width: 130 },
        { field: 'tableName', headerName: 'Table', width: 130 },
        { field: 'primaryKey', headerName: 'Primary Key', width: 130 },
        { field: 'columnName', headerName: 'Column', width: 130 },
        { field: 'value', headerName: 'Value', width: 130 },
        { field: 'q1', headerName: 'Q1', width: 150 },
        { field: 'q2', headerName: 'Q2', width: 150 },
        { field: 'q3', headerName: 'Q3', width: 150 },
        { field: 'q4', headerName: 'Q4', width: 150 },
        {
            field: 'reviewQ1',
            headerName: 'Review Q1',
            width: 200,
            renderCell: (params) => (
                <TextField
                    fullWidth
                    value={params.row.reviewQ1 || ''}
                    onChange={(e) => handleCommentChange(params.row.id, 'reviewQ1', e.target.value)}
                    disabled={params.row.alreadyCommitted}
                />
            )
        },
        {
            field: 'reviewQ2',
            headerName: 'Review Q2',
            width: 200,
            renderCell: (params) => (
                <TextField
                    fullWidth
                    value={params.row.reviewQ2 || ''}
                    onChange={(e) => handleCommentChange(params.row.id, 'reviewQ2', e.target.value)}
                    disabled={params.row.alreadyCommitted}
                />
            )
        },
        {
            field: 'reviewQ3',
            headerName: 'Review Q3',
            width: 200,
            renderCell: (params) => (
                <TextField
                    fullWidth
                    value={params.row.reviewQ3 || ''}
                    onChange={(e) => handleCommentChange(params.row.id, 'reviewQ3', e.target.value)}
                    disabled={params.row.alreadyCommitted}
                />
            )
        },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 130,
            renderCell: (params) => (
                <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleCommit(params.row.id)}
                    disabled={params.row.alreadyCommitted}
                >
                    {params.row.alreadyCommitted ? 'Committed' : 'Commit'}
                </Button>
            )
        }
    ];

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    const rows = data?.getReviewQueue || [];

    return (
        <div style={{ height: 600, width: '100%' }}>
            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{
                    pagination: {
                        paginationModel: { pageSize: 10, page: 0 },
                    },
                }}
                pageSizeOptions={[10]}
                disableRowSelectionOnClick
            />
        </div>
    );
};

export default ReviewQueueTable;

#graphql/queries.ts
import { gql } from '@apollo/client';

export const GET_USER_TABLES_DATA = gql`
  query GetUserTablesData($username: String!) {
    getUserTablesData(username: $username) {
      userName
      tableName
      primaryKey
      data
      comments
    }
  }
`;

export const UPDATE_DATA = gql`
  mutation UpdateData($input: DataInput!) {
    updateData(input: $input) {
      userName
      tableName
      primaryKey
      data
      comments
    }
  }
`;

export const UPDATE_COMMENT = gql`
  mutation UpdateComment($input: CommentInput!) {
    updateComment(input: $input) {
      userName
      tableName
      primaryKey
      data
      comments
    }
  }
`;

export const SUBMIT_FOR_REVIEW = gql`
  mutation SubmitForReview($username: String!) {
    submitForReview(username: $username)
  }
`;

export const GET_REVIEW_QUEUE = gql`
  query GetReviewQueue {
    getReviewQueue {
      id
      userName
      tableName
      primaryKey
      columnName
      value
      q1
      q2
      q3
      q4
      reviewQ1
      reviewQ2
      reviewQ3
      alreadyCommitted
    }
  }
`;

export const UPDATE_COMMENT_REVIEW = gql`
  mutation UpdateCommentReview($input: ReviewCommentInput!) {
    updateCommentReview(input: $input) {
      id
      reviewQ1
      reviewQ2
      reviewQ3
    }
  }
`;

export const MARK_REVIEW_AS_COMMITTED = gql`
  mutation MarkReviewAsCommitted($id: Int!) {
    markReviewAsCommitted(id: $id) {
      id
      alreadyCommitted
    }
  }
`; 

#pages/CommitReviewPage.tsx
import React from 'react';
import { Container } from '@mui/material';
import ReviewQueueTable from '../components/QueueReviewTable';

const CommitReviewPage: React.FC = () => {
    return (
        <Container>
            <div style={{ marginBottom: '20px' }}>
                <h1>Commit Reviews</h1>
            </div>
            <ReviewQueueTable />
        </Container>
    );
};

export default CommitReviewPage; 

#pages/HomePage.tsx
import React from 'react';
import { Typography, Paper } from '@mui/material';

const HomePage: React.FC = () => {
    return (
        <Paper style={{ padding: 20, marginTop: 20 }}>
            <Typography variant="h4" gutterBottom>
                Welcome to Data Review App
            </Typography>
            <Typography variant="body1">
                Use the navigation menu above to access different sections of the application.
                Click on "Review" to start reviewing data.
            </Typography>
        </Paper>
    );
};

export default HomePage; 

#pages/ReviewPage.tsx   
import React from 'react';
import { Container, Button } from '@mui/material';
import { DataTable } from '../components/DataTable';
import { useMutation } from '@apollo/client';
import { SUBMIT_FOR_REVIEW } from '../graphql/queries';

interface SubmitForReviewResponse {
    submitForReview: boolean;
}

const ReviewPage: React.FC = () => {
    const username = "testuser"; // Replace with actual username from your auth system
    const [submitForReview, { loading }] = useMutation<SubmitForReviewResponse>(SUBMIT_FOR_REVIEW);

    const handleSubmitForReview = async () => {
        try {
            const { data } = await submitForReview({
                variables: { username }
            });
            
            if (data?.submitForReview) {
                alert('Successfully submitted for review!');
            }
        } catch (error) {
            console.error('Error submitting for review:', error);
            alert('Error submitting for review');
        }
    };

    return (
        <Container>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1>Review Data</h1>
                <Button 
                    variant="contained" 
                    color="primary" 
                    onClick={handleSubmitForReview}
                    disabled={loading}
                >
                    {loading ? 'Submitting...' : 'Submit for Review'}
                </Button>
            </div>
            <DataTable username='admin_user' />
        </Container>
    );
};

export default ReviewPage;

#App.tsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ReviewPage from './pages/ReviewPage';
import CommitReviewPage from './pages/CommitReviewPage';
import Layout from './components/Layout';

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/review" element={<ReviewPage />} />
                <Route path="/commit" element={<CommitReviewPage />} />
            </Routes>
        </Layout>
    );
}

export default App;

#index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import App from './App';
import { client } from './apollo-client';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ApolloProvider client={client}>
        <App />
      </ApolloProvider>
    </BrowserRouter>
  </React.StrictMode>
); 

#types.ts
export interface TableData {
    userName: string;
    tableName: string;
    primaryKey: string;
    data: Record<string, any>;
    comments: {
        [column: string]: {
            [question: string]: string;
        };
    };
}

export interface UpdateDataInput {
    username: string;
    tableName: string;
    primaryKey: string;
    columnName: string;
    value: string;
}

export interface ReviewQueueItem {
  id: string;
  username: string;
  tableName: string;
  primaryKey: string;
  columnName: string;
  value: string;
  q1: string;
  q2: string;
  q3: string;
  q4: string;
  reviewQ1: string;
  reviewQ2: string;
  reviewQ3: string;
  alreadyCommitted: boolean;
}

export interface UpdateReviewAnswerInput {
  id: string;
  field: string;
  value: string;
} 
#models.py
from sqlalchemy import Column, String, JSON, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserCache(Base):
    __tablename__ = 'user_cache'
    __table_args__ = {'schema': 'development'}

    user_name = Column(String(255), primary_key=True)
    table_name = Column(String(255), primary_key=True)
    primary_key = Column(String(255), primary_key=True)
    data = Column(JSON)
    comments = Column(JSON)

    def __repr__(self):
        return f"<UserCache(user_name='{self.user_name}', table_name='{self.table_name}', primary_key='{self.primary_key}', data={self.data}, comments={self.comments})>"

    @classmethod
    def get_user_tables_data(cls, session, username: str):
        """
        Get all cache records for a given username.
        
        Args:
            session: SQLAlchemy session
            username (str): Username to filter by
            
        Returns:
            list[UserCache]: List of matching cache records
        """
        print(f"Getting data for user: {username}")
        result = session.query(cls).filter(
            cls.user_name == 'admin_user'
        ).all()
        
        return result

    @classmethod
    def update_data(cls, session, username: str, table_name: str, primary_key: str, column_name: str, value: any):
        """
        Upsert data for a specific column in the cache.
        
        Args:
            session: SQLAlchemy session
            username (str): Username
            table_name (str): Name of the table
            primary_key (str): Primary key value
            column_name (str): Column to update
            value: Value to set for the column
        """
        # Try to get existing record
        record = session.query(cls).filter_by(
            user_name=username,
            table_name=table_name,
            primary_key=primary_key
        ).first()

        if record:
            # Update existing record
            if record.data is None:
                record.data = {}
            # Create a new dictionary with existing data
            new_data = dict(record.data)
            # Update the specific column
            new_data[column_name] = value
            # Assign the updated dictionary back to record.data
            record.data = new_data
        else:
            # Create new record
            record = cls(
                user_name=username,
                table_name=table_name,
                primary_key=primary_key,
                data={column_name: value},
                comments={}
            )
            session.add(record)
        
        session.commit()
        return record

    @classmethod
    def update_comment(cls, session, username: str, table_name: str, primary_key: str, 
                      column_name: str, question: str, answer: str):
        """
        Upsert a comment for a specific column in the cache.
        """
        print(f"Updating comment with: username={username}, table={table_name}, key={primary_key}")
        print(f"Column: {column_name}, Question: {question}, Answer: {answer}")
        
        try:
            record = session.query(cls).filter_by(
                user_name=username,
                table_name=table_name,
                primary_key=primary_key
            ).first()

            if record:
                print(f"Record found: {record}")
                print(f"Current comments: {record.comments}")
                
                if record.comments is None:
                    record.comments = {}
                new_comments = dict(record.comments)
                
                # Initialize or reset column comments
                if column_name not in new_comments:
                    new_comments[column_name] = {}
                else:
                    # Keep only q1-q4 keys, remove old structure
                    old_comments = new_comments[column_name]
                    new_comments[column_name] = {
                        k: v for k, v in old_comments.items() 
                        if k in ['q1', 'q2', 'q3', 'q4']
                    }
                        
                # Store answer directly under the question key
                new_comments[column_name][question] = answer
                
                # Explicitly mark as modified
                record.comments = new_comments
                session.add(record)
                
                print(f"New comments structure: {new_comments}")
                print(f"Record before commit: {record}")
                
                session.flush()  # Flush changes to DB
                session.commit()  # Commit transaction
                
                # Verify the update
                session.refresh(record)
                print(f"Record after commit and refresh: {record}")
                
                return record
        except Exception as e:
            print(f"Error updating comment: {e}")
            session.rollback()
            raise

class ReviewQueue(Base):
    __tablename__ = 'review_queue'
    __table_args__ = {'schema': 'development'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    primary_key = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=False)
    value = Column(String)
    q1 = Column(String)
    q2 = Column(String)
    q3 = Column(String)
    q4 = Column(String)
    review_q1 = Column(String)
    review_q2 = Column(String)
    review_q3 = Column(String)
    already_committed = Column(Boolean, default=False)

    @classmethod
    def submit_for_review(cls, session, username: str):
        """
        Copy data from UserCache to ReviewQueue for review
        """
        print("Submit for review called")
        try:
            # Get all cache records for the user
            cache_records = session.query(UserCache).filter(
                UserCache.user_name == 'admin_user'
            ).all()
            print(f"cache records:{cache_records}")
            # Create review queue entries
            for cache in cache_records:
                print(f"cache:{cache}")
                if cache.data:
                    for column_name, value in cache.data.items():
                        # Get comments for this column if they exist
                        comments = cache.comments.get(column_name, {}) if cache.comments else {}
                        print(f"Comments:{comments}")
                        review = cls(
                            user_name=cache.user_name,
                            table_name=cache.table_name,
                            primary_key=cache.primary_key,
                            column_name=column_name,
                            value=str(value),
                            q1=comments.get('q1'),
                            q2=comments.get('q2'),
                            q3=comments.get('q3'),
                            q4=comments.get('q4')
                        )
                        session.add(review)
                    
            session.flush()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error submitting for review: {e}")
            raise

    @classmethod
    def get_pending_reviews(cls, session):
        """
        Get all pending review items
        """
        return session.query(cls).filter(
            cls.already_committed == False
        ).all()

    @classmethod
    def update_review(cls, session, id: int, field: str, value: str):
        """
        Update a review answer
        """
        try:
            review = session.query(cls).filter(cls.id == id).first()
            if review:
                setattr(review, field, value)
                session.commit()
                return review
            return None
        except Exception as e:
            session.rollback()
            print(f"Error updating review: {e}")
            raise

    @classmethod
    def update_comment_review(cls, session, id: int, question: str, answer: str):
        """
        Update a review answer, similar to update_comment
        """
        print(f"Updating review comment with: id={id}")
        print(f"Question: {question}, Answer: {answer}")
        
        try:
            record = session.query(cls).filter(cls.id == id).first()

            if record:
                print(f"Review record found: {record}")
                
                # Map question to corresponding field
                field_mapping = {
                    'reviewQ1': 'review_q1',
                    'reviewQ2': 'review_q2',
                    'reviewQ3': 'review_q3'
                }
                
                field = field_mapping.get(question)
                if field:
                    setattr(record, field, answer)
                    session.flush()
                    session.commit()
                    session.refresh(record)
                    print(f"Record after update: {record}")
                    return record
                else:
                    raise ValueError(f"Invalid question: {question}")
                    
        except Exception as e:
            print(f"Error updating review comment: {e}")
            session.rollback()
            raise

    @classmethod
    def mark_as_committed(cls, session, id: int):
        """
        Mark a review as committed
        """
        try:
            record = session.query(cls).filter(cls.id == id).first()
            if record:
                record.already_committed = True
                session.commit()
                return record
            return None
        except Exception as e:
            session.rollback()
            print(f"Error marking as committed: {e}")
            raise

    
#schema.py
import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from models import UserCache, ReviewQueue
from database import get_session
from strawberry.types import Info
from typing import Any

# Input types for mutations
@strawberry.input
class DataInput:
    username: str
    table_name: str
    primary_key: str
    column_name: str
    value: str

@strawberry.input
class CommentInput:
    username: str
    table_name: str
    primary_key: str
    column_name: str
    question: str
    answer: str

@strawberry.input
class UpdateReviewInput:
    id: int
    field: str
    value: str

@strawberry.input
class ReviewCommentInput:
    id: int
    question: str
    answer: str

# Types for responses
@strawberry.type
class CacheData:
    user_name: str
    table_name: str
    primary_key: str
    data: Optional[strawberry.scalars.JSON] = None
    comments: Optional[strawberry.scalars.JSON] = None

@strawberry.type
class ReviewQueueItem:
    id: int
    user_name: str
    table_name: str
    primary_key: str
    column_name: str
    value: Optional[str]
    q1: Optional[str]
    q2: Optional[str]
    q3: Optional[str]
    q4: Optional[str]
    review_q1: Optional[str]
    review_q2: Optional[str]
    review_q3: Optional[str]
    already_committed: bool

@strawberry.type
class Query:
    @strawberry.field
    def get_user_tables_data(
        self, 
        username: str,
        info: Info
    ) -> List[CacheData]:
        session = info.context["session"]
        records = UserCache.get_user_tables_data(
            session=session,
            username=username
        )
        return [
            CacheData(
                user_name=record.user_name,
                table_name=record.table_name,
                primary_key=record.primary_key,
                data=record.data,
                comments=record.comments
            ) for record in records
        ]

    @strawberry.field
    def get_review_queue(self, info: Info) -> List[ReviewQueueItem]:
        session = info.context["session"]
        reviews = ReviewQueue.get_pending_reviews(session)
        return [
            ReviewQueueItem(
                id=review.id,
                user_name=review.user_name,
                table_name=review.table_name,
                primary_key=review.primary_key,
                column_name=review.column_name,
                value=review.value,
                q1=review.q1,
                q2=review.q2,
                q3=review.q3,
                q4=review.q4,
                review_q1=review.review_q1,
                review_q2=review.review_q2,
                review_q3=review.review_q3,
                already_committed=review.already_committed
            ) for review in reviews
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_data(
        self, 
        input: DataInput,
        info: Info
    ) -> CacheData:

        session = info.context["session"]
        record = UserCache.update_data(
            session=session,
            username=input.username,
            table_name=input.table_name,
            primary_key=input.primary_key,
            column_name=input.column_name,
            value=input.value
        )

        return CacheData(
            user_name=record.user_name,
            table_name=record.table_name,
            primary_key=record.primary_key,
            data=record.data,
            comments=record.comments
        )

    @strawberry.mutation
    def update_comment(
        self, 
        input: CommentInput,
        info: Info
    ) -> CacheData:
        session = info.context["session"]
        print("update_comment called")
        print(input)
        record = UserCache.update_comment(
            session=session,
            username=input.username,
            table_name=input.table_name,
            primary_key=input.primary_key,
            column_name=input.column_name,
            question=input.question,
            answer=input.answer
        )
        return CacheData(
            user_name=record.user_name,
            table_name=record.table_name,
            primary_key=record.primary_key,
            data=record.data,
            comments=record.comments
        )

    @strawberry.mutation
    def submit_for_review(self, username: str, info: Info) -> bool:
        session = info.context["session"]
        return ReviewQueue.submit_for_review(session, username)

    @strawberry.mutation
    def update_review(self, input: UpdateReviewInput, info: Info) -> Optional[ReviewQueueItem]:
        session = info.context["session"]
        review = ReviewQueue.update_review(
            session,
            id=input.id,
            field=input.field,
            value=input.value
        )
        if review:
            return ReviewQueueItem(
                id=review.id,
                user_name=review.user_name,
                table_name=review.table_name,
                primary_key=review.primary_key,
                column_name=review.column_name,
                value=review.value,
                q1=review.q1,
                q2=review.q2,
                q3=review.q3,
                q4=review.q4,
                review_q1=review.review_q1,
                review_q2=review.review_q2,
                review_q3=review.review_q3,
                already_committed=review.already_committed
            )
        return None

    @strawberry.mutation
    def update_comment_review(
        self, 
        input: ReviewCommentInput,
        info: Info
    ) -> Optional[ReviewQueueItem]:
        session = info.context["session"]
        print("update_comment_review called")
        print(input)
        record = ReviewQueue.update_comment_review(
            session=session,
            id=input.id,
            question=input.question,
            answer=input.answer
        )
        if record:
            return ReviewQueueItem(
                id=record.id,
                user_name=record.user_name,
                table_name=record.table_name,
                primary_key=record.primary_key,
                column_name=record.column_name,
                value=record.value,
                q1=record.q1,
                q2=record.q2,
                q3=record.q3,
                q4=record.q4,
                review_q1=record.review_q1,
                review_q2=record.review_q2,
                review_q3=record.review_q3,
                already_committed=record.already_committed
            )
        return None

    @strawberry.mutation
    def mark_review_as_committed(
        self, 
        id: int,
        info: Info
    ) -> Optional[ReviewQueueItem]:
        session = info.context["session"]
        record = ReviewQueue.mark_as_committed(session, id)
        if record:
            return ReviewQueueItem(
                id=record.id,
                user_name=record.user_name,
                table_name=record.table_name,
                primary_key=record.primary_key,
                column_name=record.column_name,
                value=record.value,
                q1=record.q1,
                q2=record.q2,
                q3=record.q3,
                q4=record.q4,
                review_q1=record.review_q1,
                review_q2=record.review_q2,
                review_q3=record.review_q3,
                already_committed=record.already_committed
            )
        return None

schema = strawberry.Schema(query=Query, mutation=Mutation) 
    
