import { IFormTemplate, FieldConfig } from '../types/form-system';
import React from 'react';

// Common fields structure for both templates
const commonFields: { [key: string]: FieldConfig } = {
  projectName: {
    id: 'project-name',
    type: 'text' as const,
    name: 'projectName',
    label: 'Project Name',
    validation: { required: true }
  },
  startDate: {
    id: 'start-date',
    type: 'date' as const,
    name: 'startDate',
    label: 'Start Date',
    validation: { required: true }
  }
};

// IT Project Template
const itTemplate: IFormTemplate = {
  id: 'it-project-initiation',
  name: 'IT Project Initiation Document',
  sections: [
    {
      id: 'header',
      type: 'rich-section',
      content: `
       <div class="section">
          <h1>IT Project Initiation Document</h1>
          <p>This document outlines the technical specifications and requirements for project {{projectName}}.</p>
          
          <div class="project-basics">
            <h2>Technical Overview</h2>
            <p>Project Name: {{projectName}}</p>
            <p>Development Start Date: {{startDate}}</p>
          </div>

          <div class="project-details">
            <h2>Technical Details</h2>
            <p>Please fill in the technical specifications below.</p>
          </div>
        </div>
      `,
      fields: commonFields,
      position: 0
    },
    {
      id: 'project-details',
      type: 'field-section',
      layout: {
        type: 'grid',
        config: { columns: 2 },
        render: (elements) => {
          return React.createElement('div', {
            style: {
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '16px'
            }
          }, elements.map(element => element.render()));
        }
      },
      fields: [
        {
          id: 'description',
          type: 'text',
          name: 'description',
          label: 'Technical Description',
          validation: { required: true }
        },
        {
          id: 'manager',
          type: 'text',
          name: 'manager',
          label: 'Technical Lead',
          validation: { required: true }
        }
      ],
      position: 1
    },
    {
      id: 'resources',
      type: 'table-section',
      label: 'Development Team Allocation',
      columns: [
        { field: 'name', header: 'Developer Name', type: 'text' },
        {
          field: 'role', header: 'Technical Role', type: 'select',
          options: {
            items: [
              { value: 'dev', label: 'Developer' },
              { value: 'qa', label: 'QA Engineer' }
            ]
          }
        },
        { field: 'allocation', header: 'Sprint Allocation %', type: 'number' }
      ],
      position: 2,
      repeat: true
    }
  ],
  queries: {
    fetch: `
      query GetProjectData($dept: String!, $project: String!) {
        projectData(dept: $dept, project: $project) {
          projectName
          startDate
          description
          manager
          resources {
            name
            role
            allocation
          }
        }
      }
    `,
    submit: `
      mutation SaveProjectData($input: ProjectDataInput!) {
        saveProjectData(input: $input) {
          success
          message
        }
      }
    `
  }
};

// HR Project Template
const hrTemplate: IFormTemplate = {
  id: 'hr-project-initiation',
  name: 'HR Project Initiation Document',
  sections: [
    {
      id: 'header',
      type: 'rich-section',
      content: `
       <div class="section">
          <h1>HR Project Initiation Document</h1>
          <p>This document outlines the human resources and organizational changes for project {{projectName}}.</p>
          
          <div class="project-basics">
            <h2>Change Management Overview</h2>
            <p>Initiative Name: {{projectName}}</p>
            <p>Implementation Date: {{startDate}}</p>
          </div>

          <div class="project-details">
            <h2>Organizational Impact</h2>
            <p>Please detail the organizational changes below.</p>
          </div>
        </div>
      `,
      fields: commonFields,
      position: 0
    },
    {
      id: 'project-details',
      type: 'field-section',
      layout: {
        type: 'grid',
        config: { columns: 2 },
        render: (elements) => {
          return React.createElement('div', {
            style: {
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '16px'
            }
          }, elements.map(element => element.render()));
        }
      },
      fields: [
        {
          id: 'description',
          type: 'text',
          name: 'description',
          label: 'Change Impact Description',
          validation: { required: true }
        },
        {
          id: 'manager',
          type: 'text',
          name: 'manager',
          label: 'Change Manager',
          validation: { required: true }
        }
      ],
      position: 1
    },
    {
      id: 'resources',
      type: 'table-section',
      label: 'Stakeholder Engagement',
      columns: [
        { field: 'name', header: 'Stakeholder Name', type: 'text' },
        {
          field: 'role', header: 'Stakeholder Role', type: 'select',
          options: {
            items: [
              { value: 'dev', label: 'Change Champion' },
              { value: 'qa', label: 'Department Lead' }
            ]
          }
        },
        { field: 'allocation', header: 'Engagement Level %', type: 'number' }
      ],
      position: 2,
      repeat: true
    }
  ],
  queries: {
    fetch: `
      query GetProjectData($dept: String!, $project: String!) {
        projectData(dept: $dept, project: $project) {
          projectName
          startDate
          description
          manager
          resources {
            name
            role
            allocation
          }
        }
      }
    `,
    submit: `
      mutation SaveProjectData($input: ProjectDataInput!) {
        saveProjectData(input: $input) {
          success
          message
        }
      }
    `
  }
};

export const createProjectInitiationTemplate = (config: { dept: string; project: string }): IFormTemplate => {
  // Select template based on department
  switch (config.dept) {
    case 'it':
      return itTemplate;
    case 'hr':
      return hrTemplate;
    default:
      return itTemplate; // Default to IT template
  }
};


#Formrenderer
import React, { forwardRef, useImperativeHandle } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { useMutation, useQuery } from '@apollo/client';
import { FormConfig } from '../types/form';
import { createProjectInitiationTemplate } from '../templates/ProjectInitiationTemplate';
import { FormBuilder } from './FormBuilder';
import { gql } from '@apollo/client';
import { Snackbar, Alert } from '@mui/material';

interface FormRendererProps {
  config: FormConfig;
  onSaveComplete?: () => void;
}

export interface FormRendererRef {
  save: () => void;
}

const FormRenderer = forwardRef<FormRendererRef, FormRendererProps>(({ config, onSaveComplete }, ref) => {
  const [showSuccess, setShowSuccess] = React.useState(false);
  const [showError, setShowError] = React.useState(false);
  
  const methods = useForm({
    defaultValues: {
      resources: [] 
    }
  });
  
  const template = createProjectInitiationTemplate({
    dept: config.dept,
    project: config.project
  });
  
  const builder = new FormBuilder(template);
  const sections = builder.build();

  // Query for initial data
  const { data: formData } = useQuery(gql`${template.queries.fetch}`, {
    variables: {
      dept: config.dept,
      project: config.project
    }
  });

  // Setup mutation for save
  const [submitForm] = useMutation(gql`${template.queries.submit}`);

  // Update form when data is loaded
  React.useEffect(() => {
    if (formData?.projectData) {
      methods.reset(formData.projectData);
    }
  }, [formData, methods]);

  const handleSave = async () => {
    try {
      console.log('Save triggered');
      const formValues = methods.getValues();
      console.log('Form values:', formValues);
      
      console.log('Executing submit mutation with query:', template.queries.submit);
      const result = await submitForm({
        variables: {
          input: {
            dept: config.dept,
            project: config.project,
            ...formValues
          }
        }
      });
      
      console.log('Mutation result:', result);
      
      if (result.data?.saveProjectData?.success) {
        setShowSuccess(true);
        onSaveComplete?.();
      } else {
        setShowError(true);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      setShowError(true);
    }
  };

  // Expose save method through ref
  useImperativeHandle(ref, () => ({
    save: handleSave
  }), [handleSave]); // Add handleSave to dependency array

  return (
    <FormProvider {...methods}>
      <form>
        {Array.from(sections.values())
          .sort((a, b) => a.position - b.position)
          .map((section, index) => (
            <React.Fragment key={section.id || `section-${index}`}>
              {section.render()}
            </React.Fragment>
          ))}
      </form>

      <Snackbar 
        open={showSuccess} 
        autoHideDuration={6000} 
        onClose={() => setShowSuccess(false)}
      >
        <Alert severity="success" onClose={() => setShowSuccess(false)}>
          Form saved successfully!
        </Alert>
      </Snackbar>

      <Snackbar 
        open={showError} 
        autoHideDuration={6000} 
        onClose={() => setShowError(false)}
      >
        <Alert severity="error" onClose={() => setShowError(false)}>
          Error saving form. Please try again.
        </Alert>
      </Snackbar>
    </FormProvider>
  );
});

export default FormRenderer; 

#APp
import React, { useState, useRef } from 'react';
import { MockedProvider } from "@apollo/client/testing";
import DropDownForm from './components/DropdownForm';
import FormRenderer, { FormRendererRef } from './core/FormRenderer';
import { gql } from '@apollo/client';
import { FormConfig } from './types/form';

// Mock the actual fetch query from ProjectInitiationTemplate
const GET_PROJECT_DATA = gql`
  query GetProjectData($dept: String!, $project: String!) {
    projectData(dept: $dept, project: $project) {
      projectName
      startDate
      description
      manager
      resources {
        name
        role
        allocation
      }
    }
  }
`;

// Add mock for save mutation
const SAVE_PROJECT_DATA = gql`
  mutation SaveProjectData($input: ProjectDataInput!) {
    saveProjectData(input: $input) {
      success
      message
    }
  }
`;

const mocks = [
  // IT Department Template Mock
  {
    request: {
      query: GET_PROJECT_DATA,
      variables: {
        dept: "it",
        project: "project1"
      }
    },
    result: {
      data: {
        projectData: {
          projectName: "IT Sample Project",
          startDate: "2024-03-20",
          description: "An IT project description",
          manager: "John Doe",
          resources: [
            {
              name: "Alice Smith",
              role: "dev",
              allocation: 100
            },
            {
              name: "Bob Johnson",
              role: "qa",
              allocation: 50
            }
          ]
        }
      }
    }
  },
  // HR Department Template Mock
  {
    request: {
      query: GET_PROJECT_DATA,
      variables: {
        dept: "hr",
        project: "project1"
      }
    },
    result: {
      data: {
        projectData: {
          projectName: "HR Sample Project",
          startDate: "2024-03-21",
          description: "A HR project description",
          manager: "Jane Smith",
          resources: [
            {
              name: "Carol Wilson",
              role: "dev",
              allocation: 75
            },
            {
              name: "David Brown",
              role: "qa",
              allocation: 25
            }
          ]
        }
      }
    }
  },
  // Save mutation mock for IT
  {
    request: {
      query: SAVE_PROJECT_DATA,
      variables: {
        input: {
          dept: "it",
          project: "project1"
        }
      }
    },
    result: {
      data: {
        saveProjectData: {
          success: true,
          message: "IT Form saved successfully"
        }
      }
    }
  },
  // Save mutation mock for HR
  {
    request: {
      query: SAVE_PROJECT_DATA,
      variables: {
        input: {
          dept: "hr",
          project: "project1"
        }
      }
    },
    result: {
      data: {
        saveProjectData: {
          success: true,
          message: "HR Form saved successfully"
        }
      }
    }
  }
];

function App() {
  const [showForm, setShowForm] = useState(false);
  const [formConfig, setFormConfig] = useState<FormConfig | null>(null);
  const formRef = useRef<FormRendererRef>(null);

  const handleLoadClick = (data: { primaryFormData: any; secondaryFormData: any }) => {
    const config: FormConfig = {
      dept: data.primaryFormData.dept,
      project: data.secondaryFormData.project,
      employee: data.primaryFormData.employee,
      office: data.primaryFormData.office,
      task: data.secondaryFormData.task
    };
    setFormConfig(config);
    setShowForm(true);
  };

  const handleSave = () => {
    console.log("Save called")
    if (formRef.current) {
      formRef.current.save();
    }
  };

  return (
    <MockedProvider mocks={mocks} addTypename={false}>
      <div>
        <DropDownForm 
          onLoad={handleLoadClick} 
          onSave={handleSave}
          isLoaded={showForm} 
        />
        {showForm && formConfig && (
          <FormRenderer 
            ref={formRef}
            config={formConfig} 
            onSaveComplete={() => console.log('Save completed')}
          />
        )}
      </div>
    </MockedProvider>
  );
}

export default App;

#Dropdownform
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
    onSave?: () => void;
    isLoaded?: boolean;
}

export default function DropDownForm({ onLoad, onSave, isLoaded = false }: DropDownFormProps) {
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
        { value: 'it', label: 'Department 1' },
        { value: 'hr', label: 'Department 2' },
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
                                    onClick={onSave}
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

#RichContentSection
import React, { useEffect, useRef } from 'react';
import { FormElement } from '../core/FormElement';
import { IRichContent, FieldConfig } from '../../../types/form-system';
import DOMPurify from 'dompurify';
import ReactDOM from 'react-dom';
import { FieldFactory } from '../../../core/FieldFactory';
import { useFormContext, FormProvider, useForm } from 'react-hook-form';
import { createRoot } from 'react-dom/client';

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
              
              const root = createRoot(fieldContainer);
              root.render(
                <FormProvider {...methods}>
                  {field.render()}
                </FormProvider>
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

#TableField
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
import { restrictToVerticalAxis } from '@dnd-kit/modifiers';
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

interface TableRow {
  id: string;
  [key: string]: any;
}

interface DraggableRowProps {
  row: TableRow & {
    remove: () => void;
    dragHandleProps: any;
  };
  columns: TableColumn[];
  register: any;
}

// Update table styles to match TanStack example
const tableStyles = {
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    border: '1px solid #e0e0e0'
  },
  th: {
    backgroundColor: '#f5f5f5',
    padding: '12px 16px',
    borderBottom: '2px solid #e0e0e0',
    borderRight: '1px solid #e0e0e0',
    textAlign: 'left' as const,
    fontWeight: 'bold',
    fontSize: '14px'
  },
  td: {
    padding: '12px 16px',
    borderBottom: '1px solid #e0e0e0',
    borderRight: '1px solid #e0e0e0',
    backgroundColor: '#fff'
  },
  dragHandle: {
    cursor: 'move',
    padding: '4px 8px',
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '20px',
    color: '#666',
    width: '100%',
    textAlign: 'center' as const
  },
  dragCell: {
    width: '60px',
    borderRight: '1px solid #e0e0e0'
  },
  actionsCell: {
    width: '60px',
    borderRight: '1px solid #e0e0e0'
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

// Create a separate cell renderer component
const TableCell = ({ column, fieldName, index }: { column: TableColumn, fieldName: string, index: number }) => {
  const { register, getValues } = useFormContext();
  const formValues = getValues();
  
  // Use the numeric index instead of trying to parse the fieldName
  const value = formValues.resources?.[index]?.[column.field];
  
  console.log('TableCell - index:', index);
  console.log('TableCell - field:', column.field);
  console.log('TableCell - value:', value);
  
  switch (column.type) {
    case 'select':
      return (
        <FormControl fullWidth size="small">
          <InputLabel>{column.header}</InputLabel>
          <Select 
            {...register(`resources.${index}.${column.field}`)}
            label={column.header}
            defaultValue={value || ""}
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
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
          {...register(`resources.${index}.${column.field}`)}
          type="number"
          size="small"
          fullWidth
          label={column.header}
          defaultValue={value || 0}
        />
      );
    default:
      return (
        <TextField
          {...register(`resources.${index}.${column.field}`)}
          size="small"
          fullWidth
          label={column.header}
          defaultValue={value || ""}
        />
      );
  }
};

// Update DraggableRow to pass the index
const DraggableRow = ({ row, columns, register, index }: DraggableRowProps & { index: number }) => {
  const { transform, transition, setNodeRef, isDragging } = useSortable({
    id: row.id,
  });

  const style: CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.8 : 1,
    zIndex: isDragging ? 1 : 0,
    position: 'relative',
    backgroundColor: isDragging ? '#f5f5f5' : '#fff'
  };

  return (
    <tr ref={setNodeRef} style={style}>
      <td style={tableStyles.td}>
        <RowDragHandle rowId={row.id} />
      </td>
      {columns.map(column => (
        <td key={column.field} style={tableStyles.td}>
          <TableCell 
            column={column} 
            fieldName={`${row.id}.${column.field}`}
            index={index}
          />
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
      const { control, getValues } = useFormContext();
      
      const { fields, append, remove, move } = useFieldArray({
        control,
        name: this.name
      });

      // Initialize table with data if empty
      React.useEffect(() => {
        const currentValues = getValues(this.name);
        console.log('TableField - Current values:', currentValues);
        
        if (Array.isArray(currentValues) && currentValues.length > 0 && fields.length === 0) {
          // Clear any existing fields
          while (fields.length > 0) {
            remove(0);
          }
          
          // Only process array entries
          const validRows = currentValues.filter((row: any, index: number) => 
            row && 
            typeof row === 'object' && 
            !Array.isArray(row) &&
            index < currentValues.length // Only take array entries, not object properties
          );
          
          console.log('TableField - Valid rows to add:', validRows);
          
          // Add each valid row
          validRows.forEach((row: any, index: number) => {
            append({
              id: `row-${index}`,
              name: row.name || '',
              role: row.role || '',
              allocation: row.allocation || 0
            });
          });
        }
      }, [append, remove, fields.length, getValues]);

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

      const handleAddRow = () => {
        const newIndex = fields.length;
        append({
          id: `row-${newIndex}`,
          name: '',
          role: '',
          allocation: 0
        });
      };

      return (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
          modifiers={[restrictToVerticalAxis]}
        >
          <div style={{ overflowX: 'auto', backgroundColor: '#fff', borderRadius: '4px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
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
                        dragHandleProps: {}
                      }}
                      columns={this.columns}
                      register={register}
                      index={index}
                    />
                  ))}
                </SortableContext>
              </tbody>
            </table>
          </div>
          <Button
            startIcon={<AddIcon />}
            onClick={handleAddRow}
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
