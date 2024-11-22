const styles = `
      <style>
        @page { margin: 1in; }
        body { 
          font-family: 'Times New Roman', Times, serif;
          line-height: 1.6;
          color: #000;
          font-size: 12pt;
        }
        
        /* Headings */
        h1 { 
          font-size: 18pt;
          text-align: center;
          margin-bottom: 24pt;
          font-weight: bold;
        }
        
        h2 { 
          font-size: 14pt;
          margin: 18pt 0 12pt 0;
          font-weight: bold;
        }
        
        /* Tables */
        table {
          width: 100%;
          border-collapse: collapse;
          margin: 12pt 0 24pt 0;
          page-break-inside: avoid;
        }
        
        th {
          background-color: #f0f0f0;
          font-weight: bold;
          text-align: left;
          padding: 8pt;
          border: 1pt solid #000;
        }
        
        td {
          padding: 8pt;
          border: 1pt solid #000;
        }
        
        /* Table Caption */
        .table-caption {
          font-weight: bold;
          margin: 12pt 0 6pt 0;
          page-break-after: avoid;
        }
        
        /* Remove unwanted elements */
        .MuiTablePagination-root,
        .MuiCheckbox-root,
        .MuiButtonBase-root,
        .drag-handle,
        td:first-child,
        td:nth-child(2),
        td:last-child,
        th:first-child,
        th:nth-child(2),
        th:last-child {
          display: none !important;
        }
        
        /* Page break utilities */
        .page-break {
          page-break-before: always;
        }
      </style>
    `;

    // Clone the content and modify it for export
    const contentClone = contentRef.current.cloneNode(true);
    
    // Remove unwanted elements
    const elementsToRemove = [
      '.MuiTablePagination-root',
      '.MuiCheckbox-root',
      '.MuiButtonBase-root',
      '.drag-handle',
      '.MuiToolbar-root'
    ];
    
    elementsToRemove.forEach(selector => {
      const elements = contentClone.querySelectorAll(selector);
      elements.forEach(el => el.parentNode.removeChild(el));
    });

    // Add table captions
    const tables = contentClone.getElementsByTagName('table');
    Array.from(tables).forEach((table, index) => {
      const caption = document.createElement('div');
      caption.className = 'table-caption';
      caption.textContent = `Table ${index + 1}: Order Details`;
      table.parentNode.insertBefore(caption, table);
    });

    // Format the document
    const header = `
      <!DOCTYPE html>
      <html xmlns:o='urn:schemas-microsoft-com:office:office' 
            xmlns:w='urn:schemas-microsoft-com:office:word' 
            xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <meta charset='utf-8'>
        <title>Order Management Report</title>
        ${styles}
      </head>
      <body>
        <h1>Order Management System Report</h1>
    `;
    
    const footer = `
        </body>
      </html>
    `;

    const sourceHTML = header + contentClone.innerHTML + footer;

    // Create the download link
    const source = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(sourceHTML);
    const fileDownload = document.createElement("a");
    document.body.appendChild(fileDownload);
    fileDownload.href = source;
    fileDownload.download = `order-management-report.doc`;
    fileDownload.click();
    document.body.removeChild(fileDownload);

/* File: ./src/utils/generateColumnsConfig.js */
// src/utils/generateColumnsConfig.js
import EditableCell from '../components/EditableCell';

export const generateColumnsConfig = (columns) => {
  const config = columns.map((col) => {
    const columnConfig = {
      accessorKey: col.accessor,
      header: col.header,
    };
    if (col.editable) {
      columnConfig.cell = (props) => (
        <EditableCell {...props} updateData={props.table.options.meta.updateData} />
      );
    }
    return columnConfig;
  });

  return config;
};
-e 

/* File: ./src/components/OrdersTable.js */
// src/components/OrdersTable.js
import React from 'react';
import { useQuery, useMutation } from '@apollo/client';
import DataTable from './DataTable';
import { tableMetadata } from '../configs/tableMetadata';
import { generateColumnsConfig } from '../utils/generateColumnsConfig';

// Import GraphQL queries and mutations for the Orders table
import {
  GET_ORDERS,
  ADD_ORDER,
  UPDATE_ORDER,
} from '../graphql/ordersQueries';

const OrdersTable = () => {
  const tableConfig = tableMetadata.orders;
  const columnsConfig = generateColumnsConfig(tableConfig.columns);
  
  return (
    
      <DataTable
        tableConfig={tableConfig}
        columnsConfig={columnsConfig}
        getDataQuery={GET_ORDERS}
        addDataMutation={ADD_ORDER}
        updateDataMutation={UPDATE_ORDER}
      />
    
  );
};
  


export default OrdersTable;
-e 

/* File: ./src/components/columnsConfig.js */
// src/components/columnsConfig.js
import EditableCell from './EditableCell';

const columnsConfig = [
  {
    accessorKey: 'id',
    header: 'ID',
  },
  {
    accessorKey: 'customerName',
    header: 'Customer Name',
    cell: EditableCell,
  },
  {
    accessorKey: 'orderDate',
    header: 'Order Date',
    cell: EditableCell,
  },
  {
    id: 'actions',
    header: 'Actions',
    cell: ({ row }) => (
      <button onClick={() => row.original.handleSave()}>Save</button>
    ),
  },
];

export default columnsConfig;
-e 

/* File: ./src/components/cells/TemplateCell.js */
// src/components/cells/TemplateCell.js
import React, { useState } from 'react';
import { Box, TextField, Typography } from '@mui/material';

const TemplateCell = ({ row, getValue, table, config, column }) => {
  const value = getValue() || {};
  const [fieldValue, setFieldValue] = useState(value);

  if (!config?.template) return null;

  return (
    <Box display="flex" flexDirection="column" gap={1}>
      {config.template.map((line, lineIndex) => (
        <Box
          key={`line-${lineIndex}`}
          display="flex"
          alignItems="center"
          gap={1}
        >
          {line.map((part, index) => {
            if (part.type === 'static') {
              return (
                <Typography key={`static-${index}`} sx={part.sx}>
                  {part.content}
                </Typography>
              );
            }
            return (
              <TextField
                key={`field-${index}`}
                value={fieldValue[part.name] || ''}
                onChange={(e) => {
                  const newValue = {
                    ...fieldValue,
                    [part.name]: e.target.value,
                  };
                  setFieldValue(newValue);
                  table.options.meta?.updateData(row.index, column.id, newValue);
                }}
                size="small"
                sx={{ width: part.width }}
              />
            );
          })}
        </Box>
      ))}
    </Box>
  );
};

export default TemplateCell;
-e 

/* File: ./src/components/cells/StatusCell.js */
// src/components/cells/StatusCell.js
import React, { useState } from 'react';
import { Select, MenuItem } from '@mui/material';

const StatusCell = ({ row, getValue, table, options, column }) => {
  const value = getValue();
  const [status, setStatus] = useState(value || '');

  return (
    <Select
      value={status}
      onChange={(e) => {
        setStatus(e.target.value);
        table.options.meta?.updateData(row.index, column.id, e.target.value);
      }}
      size="small"
      fullWidth
    >
      {options.map((option) => (
        <MenuItem key={option.value} value={option.value}>
          {option.label}
        </MenuItem>
      ))}
    </Select>
  );
};

export default StatusCell;
-e 

/* File: ./src/components/cells/DateCell.js */
// src/components/cells/DateCell.js
import React, { useState } from 'react';
import { TextField } from '@mui/material';

const DateCell = ({ row, getValue, table, column }) => {
  const value = getValue();
  const [date, setDate] = useState(value || '');

  return (
    <TextField
      type="date"
      value={date}
      onChange={(e) => {
        setDate(e.target.value);
        table.options.meta?.updateData(row.index, column.id, e.target.value);
      }}
      size="small"
      fullWidth
      InputLabelProps={{ shrink: true }}
    />
  );
};

export default DateCell;
-e 

/* File: ./src/components/TableToolbar.js */
// src/components/TableToolbar.js
import React from 'react';
import { Toolbar, Typography, Box, Button } from '@mui/material';
import { alpha } from '@mui/material/styles';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';

const TableToolbar = ({ numSelected, onDeleteSelected, onAdd, title }) => {
  return (
    <Toolbar
      sx={{
        pl: { sm: 2 },
        pr: { xs: 1, sm: 1 },
        ...(numSelected > 0 && {
          bgcolor: (theme) =>
            alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
        }),
      }}
    >
      {numSelected > 0 ? (
        <Typography sx={{ flex: '1 1 100%' }} color="inherit" variant="subtitle1">
          {numSelected} selected
        </Typography>
      ) : (
        <Box sx={{ flex: '1 1 100%' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={onAdd}
            size="small"
          >
            Add New {title}
          </Button>
        </Box>
      )}
      {numSelected > 0 && (
        <Button
          color="error"
          startIcon={<DeleteIcon />}
          onClick={onDeleteSelected}
        >
          Delete
        </Button>
      )}
    </Toolbar>
  );
};

export default TableToolbar;
-e 

/* File: ./src/components/DataTable.js */
// src/components/DataTable.js
import React, { useMemo, useState, useEffect } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper, // Import createColumnHelper
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Box,
  TablePagination,
  CircularProgress,
  Typography,
  Checkbox,
} from '@mui/material';
import { DndContext, closestCenter } from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';

import DraggableRow from './DraggableRow';
import TableToolbar from './TableToolbar';
import StaticContent from './StaticContent';
import useDragAndDrop from '../hooks/useDragAndDrop';
import { useQuery, useMutation } from '@apollo/client';
import { createOrderColumns } from '../configs/createOrderColumns';

const DataTable = ({
  tableConfig,
  getDataQuery,
  addDataMutation,
  updateDataMutation,
}) => {
  const { title, description, dataAccessor } = tableConfig;

  const { loading, error, data } = useQuery(getDataQuery);
  const [addData] = useMutation(addDataMutation);
  const [updateData] = useMutation(updateDataMutation);

  const [tableData, setTableData] = useState([]);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    if (data) {
      setTableData(data[dataAccessor]);
    }
  }, [data, dataAccessor]);

  const updateRowData = (rowIndex, columnId, value) => {
    setTableData((old) =>
      old.map((row, index) => {
        if (index === rowIndex) {
          return {
            ...row,
            [columnId]: value,
          };
        }
        return row;
      })
    );
    // Do not call mutations here
  };

  const handleSave = async (row) => {
    const variables = { ...row };
    if (row.id) {
      // Update existing data
      await updateData({ variables });
    } else {
      // Add new data
      await addData({ variables });
    }
  };

  const handleAddRow = () => {
    const newRow = {
      id: '', // Temporary ID or leave empty
      customerInfo: {
        name: '',
        email: '',
      },
      orderDate: new Date().toISOString().split('T')[0], // Default to today's date
      status: 'pending', // Default status
      total: 0,
    };
    setTableData([...tableData, newRow]);
  };

  const handleDeleteSelected = () => {
    // Implement deletion logic for selected rows
    console.log('Delete selected:', selected);
    // Remove selected rows from the table data
    setTableData(tableData.filter((row) => !selected.includes(row.id)));
    setSelected([]);
  };

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelected = tableData.map((n) => n.id);
      setSelected(newSelected);
      return;
    }
    setSelected([]);
  };

  const handleSelect = (id, checked) => {
    setSelected((prevSelected) => {
      if (checked) {
        return [...prevSelected, id];
      } else {
        return prevSelected.filter((selectedId) => selectedId !== id);
      }
    });
  };

  const { sensors, handleDragEnd } = useDragAndDrop(setTableData);

  // Pagination state
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  // Create column helper
  const columnHelper = createColumnHelper();

  // Generate columnsConfig using createOrderColumns
  const columnsConfig = useMemo(
    () => createOrderColumns(columnHelper, handleSave),
    [columnHelper]
  );

  const table = useReactTable({
    data: tableData,
    columns: columnsConfig,
    state: {
      pagination,
    },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    meta: {
      updateData: updateRowData,
      handleSave: handleSave,
    },
  });

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">Error: {error.message}</Typography>;

  return (
    <Box sx={{ width: '100%' }}>
      <StaticContent title={title} description={description} />
      <Paper sx={{ width: '100%', mb: 2 }}>
        <TableToolbar
          numSelected={selected.length}
          onDeleteSelected={handleDeleteSelected}
          onAdd={handleAddRow}
          title={title}
        />
        <TableContainer>
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <Table sx={{ minWidth: 750 }}>
              <TableHead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        indeterminate={
                          selected.length > 0 && selected.length < tableData.length
                        }
                        checked={
                          tableData.length > 0 && selected.length === tableData.length
                        }
                        onChange={handleSelectAllClick}
                      />
                    </TableCell>
                    <TableCell padding="checkbox" /> {/* For drag handle */}
                    {headerGroup.headers.map((header) => (
                      <TableCell key={header.id}>
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableHead>
              <TableBody>
                <SortableContext
                  items={tableData.map((item) => item.id.toString())}
                  strategy={verticalListSortingStrategy}
                >
                  {table.getRowModel().rows.map((row) => (
                    <DraggableRow
                      key={row.original.id || row.index}
                      row={row}
                      selected={selected.includes(row.original.id)}
                      onSelect={handleSelect}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </TableCell>
                      ))}
                    </DraggableRow>
                  ))}
                </SortableContext>
              </TableBody>
            </Table>
          </DndContext>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={tableData.length}
          rowsPerPage={pagination.pageSize}
          page={pagination.pageIndex}
          onPageChange={(event, newPage) =>
            setPagination((prev) => ({ ...prev, pageIndex: newPage }))
          }
          onRowsPerPageChange={(event) => {
            const newSize = Number(event.target.value);
            setPagination({ pageIndex: 0, pageSize: newSize });
          }}
        />
      </Paper>
    </Box>
  );
};

export default DataTable;
-e 

/* File: ./src/components/EditableCell.js */
// src/components/EditableCell.js
import React, { useState, useEffect } from 'react';
import { TextField } from '@mui/material';

const EditableCell = ({ getValue, row, column, updateData }) => {
  const initialValue = getValue();
  const [value, setValue] = useState(initialValue);

  const onBlur = () => {
    updateData(row.index, column.id, value);
  };

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return (
    <TextField
      value={value || ''}
      onChange={(e) => setValue(e.target.value)}
      onBlur={onBlur}
      variant="standard"
      fullWidth
    />
  );
};

export default EditableCell;
-e 

/* File: ./src/components/DraggableRow.js */
// src/components/DraggableRow.js
import React from 'react';
import { TableRow, TableCell, Checkbox } from '@mui/material';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

const DraggableRow = ({ row, children, selected, onSelect }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: row.original.id.toString(),
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    backgroundColor: selected ? 'rgba(25, 118, 210, 0.08)' : 'inherit',
  };

  return (
    <TableRow ref={setNodeRef} style={style}>
      <TableCell padding="checkbox">
        <Checkbox
          checked={selected}
          onChange={(e) => onSelect(row.original.id, e.target.checked)}
        />
      </TableCell>
      <TableCell padding="checkbox">
        <DragIndicatorIcon
          {...attributes}
          {...listeners}
          sx={{
            cursor: 'grab',
            color: 'text.secondary',
            '&:hover': {
              color: 'text.primary',
            },
          }}
        />
      </TableCell>
      {children}
    </TableRow>
  );
};

export default DraggableRow;
-e 

/* File: ./src/components/StaticContent.js */
// src/components/StaticContent.js
import React from 'react';
import { Box, Typography } from '@mui/material';

const StaticContent = ({ title, description }) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body1" sx={{ mb: 2 }}>
        {description || 'Manage and track all data in one place'}
      </Typography>
    </Box>
  );
};

export default StaticContent;
-e 

/* File: ./src/graphql/ordersQueries.js */
// src/graphql/ordersQueries.js
import { gql } from '@apollo/client';

export const GET_ORDERS = gql`
  query GetOrders {
    orders {
      id
      customerName
      orderDate
    }
  }
`;

export const ADD_ORDER = gql`
  mutation AddOrder($customerName: String!, $orderDate: String!) {
    addOrder(customerName: $customerName, orderDate: $orderDate) {
      id
      customerName
      orderDate
    }
  }
`;

export const UPDATE_ORDER = gql`
  mutation UpdateOrder($id: ID!, $customerName: String!, $orderDate: String!) {
    updateOrder(id: $id, customerName: $customerName, orderDate: $orderDate) {
      id
      customerName
      orderDate
    }
  }
`;
-e 

/* File: ./src/graphql/productsQueries.js */
// src/graphql/productsQueries.js
import { gql } from '@apollo/client';

export const GET_PRODUCTS = gql`
  query GetProducts {
    products {
      id
      productName
      price
    }
  }
`;

export const ADD_PRODUCT = gql`
  mutation AddProduct($productName: String!, $price: Float!) {
    addProduct(productName: $productName, price: $price) {
      id
      productName
      price
    }
  }
`;

export const UPDATE_PRODUCT = gql`
  mutation UpdateProduct($id: ID!, $productName: String!, $price: Float!) {
    updateProduct(id: $id, productName: $productName, price: $price) {
      id
      productName
      price
    }
  }
`;
-e 

/* File: ./src/hooks/useDragAndDrop.js */
// src/hooks/useDragAndDrop.js
import { useSensors, useSensor, PointerSensor } from '@dnd-kit/core';

const useDragAndDrop = (setTableData) => {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (!active || !over || active.id === over.id) return;

    setTableData((items) => {
      const activeIndex = items.findIndex(
        (item) => item.id.toString() === active.id.toString()
      );
      const overIndex = items.findIndex(
        (item) => item.id.toString() === over.id.toString()
      );

      if (activeIndex === -1 || overIndex === -1) return items;

      const newItems = [...items];
      const [movedItem] = newItems.splice(activeIndex, 1);
      newItems.splice(overIndex, 0, movedItem);

      return newItems;
    });
  };

  return { sensors, handleDragEnd };
};

export default useDragAndDrop;
-e 

/* File: ./src/App.test.js */
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
-e 

/* File: ./src/configs/createOrderColumns.js */
// src/config/createOrderColumns.js
import DateCell from '../components/cells/DateCell';
import StatusCell from '../components/cells/StatusCell';
import TemplateCell from '../components/cells/TemplateCell';

// src/config/createOrderColumns.js

export const createOrderColumns = (columnHelper) => [
  // ... other columns
  columnHelper.accessor('customerInfo', {
    header: 'Customer Details',
    cell: (props) => (
      <TemplateCell
        {...props}
        config={{
          template: [
            [
              { type: 'static', content: 'Name:', sx: { fontWeight: 'bold' } },
              { type: 'field', name: 'name', width: '150px' },
            ],
            [
              { type: 'static', content: 'Email:', sx: { fontWeight: 'bold' } },
              { type: 'field', name: 'email', width: '200px' },
            ],
            // Add more lines as needed
          ],
        }}
      />
    ),
  }),
  columnHelper.accessor('order_date', {
    header: 'Order Date',
    cell: (props) => <DateCell {...props} />,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: (props) => (
      <StatusCell
        {...props}
        options={[
          { value: 'pending', label: 'Pending' },
          { value: 'confirmed', label: 'Confirmed' },
          { value: 'shipped', label: 'Shipped' },
          // Add more options as needed
        ]}
      />
    ),
  }),

  // Add actions column
  //columnHelper.display({
   // id: 'actions',
    //header: 'Actions',
    //cell: ({ row }) => (
     // <button onClick={() => handleSave(row.original)}>Save</button>
    //),
  //}),
];


-e 

/* File: ./src/configs/tableMetadata.js */
// src/configs/tableMetadata.js
export const tableMetadata = {
    orders: {
      title: 'Orders',
      dataAccessor: 'orders',
      columns: [
        { accessor: 'id', header: 'ID' },
        { accessor: 'customerName', header: 'Customer Name', editable: true },
        { accessor: 'orderDate', header: 'Order Date', editable: true },
      ],
    },
    products: {
      title: 'Products',
      dataAccessor: 'products',
      columns: [
        { accessor: 'id', header: 'ID' },
        { accessor: 'productName', header: 'Product Name', editable: true },
        { accessor: 'price', header: 'Price', editable: true },
      ],
    },
  };
  -e 

/* File: ./src/configs/formRegistery.js */

// Import other forms as needed

export const formRegistry = {
  'Template 1': {
    'Section 1': {
      forms: [],
      description: 'Template 1 Section 1 Description'
    },
    'Section 2': {
      forms: [
       // { component: OrderForm, name: 'Order Form' },
       // { component: Orders, name: 'Orders List' }
      ],
      description: 'Order Management Interface'
    },
    'Section 3': {
      forms: [],
      description: 'Template 1 Section 3 Description'
    }
  },
  'Template 2': {
    'Section 1': {
      forms: [],
      description: 'Template 2 Section 1 Description'
    },
    // Add more sections as needed
  },
  // Add more templates as needed
}; -e 

/* File: ./src/setupTests.js */
// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
-e 

/* File: ./src/App.js */
// src/App.js
import React, { useState, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Box,
  Card,
  CardHeader,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Container,
  Button,
  Stack,
} from '@mui/material';
import { Download as DownloadIcon, Save as SaveIcon } from '@mui/icons-material';
import { ApolloProvider } from '@apollo/client';
import client from './apollo_client';
import DataTable from './components/DataTable';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { tableMetadata } from './configs/tableMetadata';
import { generateColumnsConfig } from './utils/generateColumnsConfig';
import { formRegistry } from './configs/formRegistery';
// Import GraphQL queries and mutations
import OrdersTable from './components/OrdersTable';
import {
  GET_PRODUCTS,
  ADD_PRODUCT,
  UPDATE_PRODUCT,
} from './graphql/productsQueries';

const App = () => {
  const [templateSection, setTemplateSection] = useState({
    template: '',
    section: '',
  });
  const [crudSelections, setCrudSelections] = useState({
    database: '',
    environment: '',
    region: '',
    instance: '',
    version: '',
  });
  const [showContent, setShowContent] = useState(false);
  const contentRef = useRef(null);
  const templates = Object.keys(formRegistry);
  const sections = templateSection.template 
    ? Object.keys(formRegistry[templateSection.template]) 
    : [];

  const crudOptions = {
    database: ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis'],
    environment: ['Development', 'Staging', 'Production'],
    region: ['US-East', 'US-West', 'EU-Central', 'Asia-Pacific'],
    instance: ['t2.micro', 't2.small', 't2.medium', 't2.large'],
    version: ['v1.0', 'v2.0', 'v3.0', 'Latest'],
  };
  const handleTemplateSectionChange = (field) => (event) => {
    setTemplateSection(prev => ({
      ...prev,
      [field]: event.target.value,
      ...(field === 'template' ? { section: '' } : {})
    }));
    setShowContent(false);
  };
  const handleCrudChange = (field) => (event) => {
    setCrudSelections(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    setShowContent(false);
  };
  const handleSave = () => {
    // Implement save functionality
    console.log('Saving...');
  };
  const handleExport = () => {
    // Implement export functionality
    console.log('Exporting...');
  };
  const canLoadContent = templateSection.template && 
  templateSection.section;
  const handleLoadContent = () => {
    setShowContent(true);
  };

 

  return (
    <ApolloProvider client={client}>
    <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Dynamic Form System
              </Typography>
            </Toolbar>
          </AppBar>

          <Box sx={{ 
            position: 'sticky', 
            top: 0, 
            bgcolor: 'background.default',
            zIndex: 1,
            pt: 2,
            pb: 2,
            borderBottom: 1,
            borderColor: 'divider'
          }}>
            <Container maxWidth="lg">
              <Stack direction="row" spacing={2}>
                {/* Template Selection Card */}
                <Card sx={{ flexGrow: 1 }}>
                  <CardHeader 
                    title="Select Template" 
                    sx={{ bgcolor: 'primary.light', color: 'white', p: 1 }}
                  />
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <FormControl size="small" fullWidth>
                        <InputLabel>Template</InputLabel>
                        <Select
                          value={templateSection.template}
                          label="Template"
                          onChange={handleTemplateSectionChange('template')}
                        >
                          {templates.map((template) => (
                            <MenuItem key={template} value={template}>
                              {template}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      <FormControl size="small" fullWidth>
                        <InputLabel>Section</InputLabel>
                        <Select
                          value={templateSection.section}
                          label="Section"
                          onChange={handleTemplateSectionChange('section')}
                          disabled={!templateSection.template}
                        >
                          {sections.map((section) => (
                            <MenuItem key={section} value={section}>
                              {section}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Box>
                  </CardContent>
                </Card>

                {/* CRUD Operations Card */}
                <Card sx={{ flexGrow: 1 }}>
                  <CardHeader 
                    title="Configure Database" 
                    sx={{ bgcolor: 'secondary.light', color: 'white', p: 1 }}
                  />
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(3, 1fr)', 
                      gap: 1 
                    }}>
                      {Object.entries(crudOptions).map(([field, options]) => (
                        <FormControl key={field} size="small">
                          <InputLabel>{field.charAt(0).toUpperCase() + field.slice(1)}</InputLabel>
                          <Select
                            value={crudSelections[field]}
                            label={field.charAt(0).toUpperCase() + field.slice(1)}
                            onChange={handleCrudChange(field)}
                          >
                            {options.map((option) => (
                              <MenuItem key={option} value={option}>
                                {option}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      ))}
                    </Box>
                  </CardContent>
                </Card>

                {/* Actions Card */}
                <Card sx={{ width: 200 }}>
                  <CardHeader 
                    title="Actions" 
                    sx={{ bgcolor: 'success.light', color: 'white', p: 1 }}
                  />
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Stack spacing={1}>
                      <Button
                        variant="contained"
                        onClick={handleLoadContent}
                        disabled={!canLoadContent}
                        fullWidth
                      >
                        Load Content
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSave}
                        disabled={!showContent}
                        fullWidth
                      >
                        Save
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<DownloadIcon />}
                        onClick={handleExport}
                        disabled={!showContent}
                        fullWidth
                      >
                        Export
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              </Stack>
            </Container>
          </Box>
          <Container maxWidth="lg" sx={{ mt: 2 }}>
            {/* Dynamic Content */}
            <Box ref={contentRef}>
              { <OrdersTable />}
            </Box>
          </Container>
      </Box>
    </ApolloProvider>
  );
};

export default App;
-e 

