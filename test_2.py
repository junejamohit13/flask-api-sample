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

###
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
