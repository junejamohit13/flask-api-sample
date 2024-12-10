import React, { CSSProperties } from 'react';
import { 
  useReactTable, 
  getCoreRowModel,
  flexRender,
  ColumnDef 
} from '@tanstack/react-table';
import {
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
  closestCenter,
  DragEndEvent
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { BaseField } from './BaseField';
import { useFieldArray, useFormContext } from 'react-hook-form';
import { ValidationRules } from '../../../../types/form-system';
import { 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  TextField,
  IconButton,
  Button
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

interface TableColumn {
  field: string;
  header: string;
  type: 'text' | 'number' | 'date' | 'select';
  options?: {
    items: Array<{ value: string | number; label: string; }>;
  };
}

// Update table styles to match TanStack example
const tableStyles = {
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    border: '1px solid #000'
  },
  th: {
    backgroundColor: '#fff',
    padding: '12px 8px',
    borderBottom: '2px solid #000',
    borderRight: '1px solid #000',
    textAlign: 'left' as const,
    fontWeight: 'bold',
    fontSize: '14px'
  },
  td: {
    padding: '8px',
    borderBottom: '1px solid #000',
    borderRight: '1px solid #000',
    backgroundColor: '#fff'
  },
  dragHandle: {
    cursor: 'move',
    padding: '4px 8px',
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '16px',
    color: '#666',
    width: '100%',
    textAlign: 'center' as const
  },
  row: {
    '&:hover': {
      backgroundColor: '#f8f8f8'
    }
  },
  dragCell: {
    width: '40px',
    borderRight: '1px solid #000'
  },
  actionsCell: {
    width: '40px',
    borderRight: '1px solid #000'
  }
};

// Update RowDragHandle component
const RowDragHandle = ({ rowId }: { rowId: string }) => {
  const { attributes, listeners } = useSortable({
    id: rowId,
  });
  return (
    <button {...attributes} {...listeners} style={tableStyles.dragHandle}>
      ⋮⋮
    </button>
  );
};

// Draggable row component
const DraggableRow = ({ 
  row, 
  columns,
  register 
}: { 
  row: any;
  columns: TableColumn[];
  register: any;
}) => {
  const { transform, transition, setNodeRef, isDragging } = useSortable({
    id: row.id,
  });

  const style: CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.8 : 1,
    zIndex: isDragging ? 1 : 0,
    position: 'relative',
    ...tableStyles.row,
    backgroundColor: isDragging ? '#f0f0f0' : '#fff'
  };

  const renderCell = (column: TableColumn, fieldName: string) => {
    switch (column.type) {
      case 'select':
        return (
          <FormControl fullWidth size="small">
            <InputLabel>{column.header}</InputLabel>
            <Select {...register(fieldName)} label={column.header}>
              {column.options?.items.map(item => (
                <MenuItem key={item.value} value={item.value}>
                  {item.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      case 'number':
        return (
          <TextField
            {...register(fieldName)}
            type="number"
            size="small"
            fullWidth
            label={column.header}
          />
        );
      default:
        return (
          <TextField
            {...register(fieldName)}
            size="small"
            fullWidth
            label={column.header}
          />
        );
    }
  };

  return (
    <tr ref={setNodeRef} style={style}>
      <td style={tableStyles.td}>
        <button style={tableStyles.dragHandle} {...row.dragHandleProps}>
          ⋮⋮
        </button>
      </td>
      {columns.map(column => (
        <td key={column.field} style={tableStyles.td}>
          {renderCell(column, `${row.id}.${column.field}`)}
        </td>
      ))}
      <td style={tableStyles.td}>
        <IconButton size="small" onClick={row.remove}>
          <DeleteIcon />
        </IconButton>
      </td>
    </tr>
  );
};

export class TableField extends BaseField {
  constructor(
    id: string,
    type: string,
    name: string,
    label: string,
    validation?: ValidationRules,
    public columns: TableColumn[] = []
  ) {
    super(id, type, name, label, validation);
  }

  protected renderField(register: any, error?: any): JSX.Element {
    const TableFieldRenderer = () => {
      const { control } = useFormContext();
      const { fields, append, remove, move } = useFieldArray({
        control,
        name: this.name
      });

      const sensors = useSensors(
        useSensor(MouseSensor, {}),
        useSensor(TouchSensor, {}),
        useSensor(KeyboardSensor, {})
      );

      const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;
        if (active && over && active.id !== over.id) {
          const oldIndex = fields.findIndex(f => f.id === active.id);
          const newIndex = fields.findIndex(f => f.id === over.id);
          move(oldIndex, newIndex);
        }
      };

      return (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyles.table}>
              <thead>
                <tr>
                  <th style={{ ...tableStyles.th, ...tableStyles.dragCell }}>Move</th>
                  {this.columns.map(col => (
                    <th key={col.field} style={tableStyles.th}>
                      {col.header}
                    </th>
                  ))}
                  <th style={{ ...tableStyles.th, ...tableStyles.actionsCell }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                <SortableContext
                  items={fields.map(f => f.id)}
                  strategy={verticalListSortingStrategy}
                >
                  {fields.map((field, index) => (
                    <DraggableRow
                      key={field.id}
                      row={{
                        ...field,
                        remove: () => remove(index),
                        dragHandleProps: {
                          'data-handle': true
                        }
                      }}
                      columns={this.columns}
                      register={register}
                    />
                  ))}
                </SortableContext>
              </tbody>
            </table>
          </div>
          <Button
            startIcon={<AddIcon />}
            onClick={() => append({})}
            size="small"
            sx={{ mt: 2 }}
            variant="outlined"
          >
            Add Row
          </Button>
        </DndContext>
      );
    };

    return <TableFieldRenderer />;
  }
} 



#RichContentSection.tsx
import React, { useEffect, useRef } from 'react';
import { FormElement } from '../core/FormElement';
import { IRichContent, FieldConfig } from '../../../types/form-system';
import DOMPurify from 'dompurify';
import ReactDOM from 'react-dom';
import { FieldFactory } from '../../../core/FieldFactory';
import { useFormContext, FormProvider, useForm } from 'react-hook-form';

export class RichContentSection extends FormElement implements IRichContent {
  public content: {
    html: string;
    fieldPlaceholders?: any[];
  };
  private fields: Map<string, FieldConfig>;

  constructor(
    id: string,
    htmlContent: string,
    fields: { [key: string]: FieldConfig },
    position: number = 0
  ) {
    super(id, 'rich-section', id, 'Rich Content');
    this.position = position;
    this.content = {
      html: htmlContent,
      fieldPlaceholders: []
    };
    this.fields = new Map(Object.entries(fields));
  }

  private replaceFieldPlaceholders(html: string): string {
    let processedHtml = html;
    this.fields.forEach((_, placeholder) => {
      processedHtml = processedHtml.replace(
        `{{${placeholder}}}`,
        `<div data-field-placeholder="${placeholder}"></div>`
      );
    });
    return processedHtml;
  }

  render(): JSX.Element {
    const RichContentRenderer = () => {
      const containerRef = useRef<HTMLDivElement>(null);
      const methods = useForm();

      useEffect(() => {
        if (containerRef.current) {
          this.fields.forEach((fieldConfig, placeholder) => {
            const placeholderElement = containerRef.current?.querySelector(
              `[data-field-placeholder="${placeholder}"]`
            );
            if (placeholderElement) {
              const field = FieldFactory.createField(fieldConfig);
              const fieldContainer = document.createElement('div');
              placeholderElement.replaceWith(fieldContainer);
              ReactDOM.render(
                <FormProvider {...methods}>
                  {field.render()}
                </FormProvider>,
                fieldContainer
              );
            }
          });
        }
      }, []);

      const sanitizedHtml = DOMPurify.sanitize(
        this.replaceFieldPlaceholders(this.content.html)
      );

      return (
        <div 
          ref={containerRef}
          dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
          className="rich-content"
          data-testid={`rich-content-${this.id}`}
        />
      );
    };

    return <RichContentRenderer />;
  }
} 


#datefield.tsx

import React from 'react';
import { TextField } from '@mui/material';
import { BaseField } from './BaseField';
import { ValidationRules } from '../../../../types/form-system';

export class DateField extends BaseField {
  constructor(
    id: string,
    type: string,
    name: string,
    label: string,
    validation?: ValidationRules
  ) {
    super(id, type, name, label, validation);
  }

  protected renderField(register: any, error?: any): JSX.Element {
    return (
      <TextField
        {...register(this.name, this.validation)}
        type="date"
        label={this.label}
        error={!!error}
        helperText={error?.message as string}
        fullWidth
        size="small"
        InputLabelProps={{
          shrink: true,
        }}
      />
    );
  }
} 

#selectfield.tsx 
import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { BaseField } from './BaseField';
import { ValidationRules } from '../../../../types/form-system';

interface SelectOption {
  value: string | number;
  label: string;
}

export class SelectField extends BaseField {
  public defaultValue?: any;
  constructor(
    id: string,
    type: string,
    name: string,
    label: string,
    validation?: ValidationRules,
    public options: SelectOption[] = []
  ) {
    super(id, type, name, label, validation);
    
  }

  protected renderField(register: any, error?: any): JSX.Element {
    return (
      <FormControl fullWidth size="small" error={!!error}>
        <InputLabel>{this.label}</InputLabel>
        <Select
          {...register(this.name, this.validation)}
          label={this.label}
          defaultValue={this.defaultValue || ''}
        >
          <MenuItem value="">
            <em>None</em>
          </MenuItem>
          {this.options.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  }
} 


#textfield.tsx 
import React from 'react';
import { TextField as MuiTextField } from '@mui/material';
import { BaseField } from './BaseField';
import { ValidationRules } from '../../../../types/form-system';

export class TextField extends BaseField {
  constructor(
    id: string,
    type: string,
    name: string,
    label: string,
    validation?: ValidationRules
  ) {
    super(id, type, name, label, validation);
  }

  protected renderField(register: any, error?: any): JSX.Element {
    return (
      <MuiTextField
        {...register(this.name, this.validation)}
        label={this.label}
        error={!!error}
        helperText={error?.message as string}
        fullWidth
        size="small"
      />
    );
  }
} 

#FormField.tsx
import React from 'react';
import { TextField } from '@mui/material';
import { BaseField } from './fields/BaseField';
import { ValidationRules } from '../../../types/form-system';

export class FormFieldComponent extends BaseField {


  constructor(
    id: string,
    type: string,
    name: string,
    label: string,
    validation?: ValidationRules
  ) {
    super(id, type, name, label, validation);

  }

  protected renderField(register: any, error?: any): JSX.Element {
    return (
      <TextField
        {...register(this.name, this.validation)}
        label={this.label}
        error={!!error}
        helperText={error?.message as string}
        fullWidth
        size="small"
      />
    );
  }
} 

#Dropdownform.tsx
import React, { useState, useEffect } from 'react';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';

interface DropdownOption {
    value: string;
    label: string;
}

interface DropDownFormProps {
    onLoad: (data: { primaryFormData: any; secondaryFormData: any }) => void;
    isLoaded?: boolean;
}

export default function DropDownForm({ onLoad, isLoaded = false }: DropDownFormProps) {
    // First card form data
    const [primaryFormData, setPrimaryFormData] = useState({
        dept: '',
        employee: '',
        office: ''
    });

    // Second card form data
    const [secondaryFormData, setSecondaryFormData] = useState({
        project: '',
        task: ''
    });

    // Options for first card
    const deptOptions: DropdownOption[] = [
        { value: 'dept1', label: 'Department 1' },
        { value: 'dept2', label: 'Department 2' },
        { value: 'dept3', label: 'Department 3' },
    ];
    
    const employeeOptions: DropdownOption[] = [
        { value: 'emp1', label: 'Employee 1' },
        { value: 'emp2', label: 'Employee 2' },
        { value: 'emp3', label: 'Employee 3' },
    ];
    
    const officeOptions: DropdownOption[] = [
        { value: 'office1', label: 'Office 1' },
        { value: 'office2', label: 'Office 2' },
        { value: 'office3', label: 'Office 3' },
    ];

    // Options for second card (dependent on first card selections)
    const [projectOptions, setProjectOptions] = useState<DropdownOption[]>([]);
    const [taskOptions, setTaskOptions] = useState<DropdownOption[]>([]);

    // Update dependent options when primary form changes
    useEffect(() => {
        if (primaryFormData.dept && primaryFormData.employee) {
            // Example of dependent options - replace with your logic
            setProjectOptions([
                { value: 'project1', label: `Project 1 - ${primaryFormData.dept}` },
                { value: 'project2', label: `Project 2 - ${primaryFormData.dept}` },
            ]);
        }
    }, [primaryFormData.dept, primaryFormData.employee]);

    useEffect(() => {
        if (secondaryFormData.project) {
            // Example of dependent options - replace with your logic
            setTaskOptions([
                { value: 'task1', label: `Task 1 - ${secondaryFormData.project}` },
                { value: 'task2', label: `Task 2 - ${secondaryFormData.project}` },
            ]);
        }
    }, [secondaryFormData.project]);

    const handlePrimaryChange = (event: SelectChangeEvent) => {
        const { name, value } = event.target;
        setPrimaryFormData(prevData => ({
            ...prevData,
            [name]: value
        }));
    };

    const handleSecondaryChange = (event: SelectChangeEvent) => {
        const { name, value } = event.target;
        setSecondaryFormData(prevData => ({
            ...prevData,
            [name]: value
        }));
    };

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        console.log('Form submitted:', { primaryFormData, secondaryFormData });
    };

    const handleLoadClick = () => {
        onLoad({
            primaryFormData,
            secondaryFormData
        });
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ m: 2 }}>
            <Grid container spacing={2} alignItems="flex-start">
                {/* First Card */}
                <Grid item xs={12} md={5}>
                    <Card sx={{ 
                        height: '100%',
                        boxShadow: 'none',
                        backgroundColor: 'transparent'
                    }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Primary Information
                            </Typography>
                            <Box sx={{ 
                                display: 'flex', 
                                flexDirection: 'row', 
                                gap: 1,
                                flexWrap: 'nowrap'
                            }}>
                                <FormControl sx={{ minWidth: 120 }} size="small">
                                    <InputLabel>Department</InputLabel>
                                    <Select
                                        name="dept"
                                        value={primaryFormData.dept}
                                        label="Department"
                                        onChange={handlePrimaryChange}
                                    >
                                        <MenuItem value=""><em>None</em></MenuItem>
                                        {deptOptions.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <FormControl sx={{ minWidth: 120 }} size="small">
                                    <InputLabel>Employee</InputLabel>
                                    <Select
                                        name="employee"
                                        value={primaryFormData.employee}
                                        label="Employee"
                                        onChange={handlePrimaryChange}
                                    >
                                        <MenuItem value=""><em>None</em></MenuItem>
                                        {employeeOptions.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <FormControl sx={{ minWidth: 120 }} size="small">
                                    <InputLabel>Office</InputLabel>
                                    <Select
                                        name="office"
                                        value={primaryFormData.office}
                                        label="Office"
                                        onChange={handlePrimaryChange}
                                    >
                                        <MenuItem value=""><em>None</em></MenuItem>
                                        {officeOptions.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Second Card */}
                <Grid item xs={12} md={4}>
                    <Card sx={{ 
                        height: '100%',
                        boxShadow: 'none',
                        backgroundColor: 'transparent'
                    }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Project Details
                            </Typography>
                            <Box sx={{ 
                                display: 'flex', 
                                flexDirection: 'row', 
                                gap: 1,
                                flexWrap: 'nowrap'
                            }}>
                                <FormControl sx={{ minWidth: 120 }} size="small">
                                    <InputLabel>Project</InputLabel>
                                    <Select
                                        name="project"
                                        value={secondaryFormData.project}
                                        label="Project"
                                        onChange={handleSecondaryChange}
                                    >
                                        <MenuItem value=""><em>None</em></MenuItem>
                                        {projectOptions.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <FormControl sx={{ minWidth: 120 }} size="small">
                                    <InputLabel>Task</InputLabel>
                                    <Select
                                        name="task"
                                        value={secondaryFormData.task}
                                        label="Task"
                                        onChange={handleSecondaryChange}
                                    >
                                        <MenuItem value=""><em>None</em></MenuItem>
                                        {taskOptions.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                {option.label}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Modified Load Button card with horizontal buttons */}
                <Grid item xs={12} md={3}>
                    <Card sx={{ 
                        height: '100%', 
                        backgroundColor: 'transparent', 
                        boxShadow: 'none'
                    }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Load Templates
                            </Typography>
                            <Box sx={{ 
                                display: 'flex', 
                                flexDirection: 'row', 
                                gap: 1,
                                flexWrap: 'nowrap'
                            }}>
                                <Button 
                                    variant="contained" 
                                    size="small" 
                                    onClick={handleLoadClick}
                                >
                                    Load
                                </Button>
                                <Button 
                                    variant="contained" 
                                    size="small" 
                                    disabled={!isLoaded}
                                    onClick={() => console.log('Save clicked')}
                                >
                                    Save
                                </Button>
                                <Button 
                                    variant="contained" 
                                    size="small" 
                                    disabled={!isLoaded}
                                    onClick={() => console.log('Export clicked')}
                                >
                                    Export
                                </Button>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
