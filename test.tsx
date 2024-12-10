FieldFactory.ts
import { IField, ValidationRules } from '../types/form-system';
import { TextField } from '../components/Form/components/fields/TextField';
import { DateField } from '../components/Form/components/fields/DateField';
import { SelectField } from '../components/Form/components/fields/SelectField';
import { TableField } from '../components/Form/components/fields/TableField';

type FieldConstructor = new (
  id: string,
  type: string,
  name: string,
  label: string,
  validation?: ValidationRules
) => IField;

export class FieldFactory {
  private static fieldTypes = new Map<string, FieldConstructor>();

  static registerField(type: string, fieldClass: FieldConstructor) {
    this.fieldTypes.set(type, fieldClass);
  }

  static createField(config: {
    type: string;
    id: string;
    name: string;
    label: string;
    validation?: ValidationRules;
    options?: any;
  }): IField {
    const FieldClass = this.fieldTypes.get(config.type);
    if (!FieldClass) {
      throw new Error(`Unknown field type: ${config.type}`);
    }

    switch (config.type) {
      case 'table':
        return new TableField(
          config.id,
          'table',
          config.name,
          config.label,
          config.validation,
          config.options?.columns || []
        );
      default:
        return new FieldClass(
          config.id,
          config.type,
          config.name,
          config.label,
          config.validation
        );
    }
  }
}

// Register default field types
FieldFactory.registerField('text', TextField);
FieldFactory.registerField('date', DateField);
FieldFactory.registerField('select', SelectField);
FieldFactory.registerField('table', TableField); 


#FormBuilder.ts
import React from 'react';
import { IFormTemplate, FormSection as IFormSection, RichSection, FieldSection, TableSection, IFormElement } from '../types/form-system';
import { FieldFactory } from './FieldFactory';
import { FormSection } from './FormSection';
import { FormLayout } from '../components/Form/layouts/FormLayout';
import { RichContentSection } from '../components/Form/components/RichContentSection';

export class FormBuilder {
  private template: IFormTemplate;
  private sections: Map<string, FormSection> = new Map();

  constructor(template: IFormTemplate) {
    this.template = template;
  }

  private buildSection(sectionConfig: IFormSection): FormSection {
    console.log("Building section of type:", sectionConfig.type);
    switch (sectionConfig.type) {
      case 'rich-section':
        return this.buildRichSection(sectionConfig as RichSection);
      case 'field-section':
        return this.buildFieldSection(sectionConfig as FieldSection);
      case 'table-section':
        return this.buildTableSection(sectionConfig as TableSection);
      default:
        throw new Error(`Unknown section type:`);
    }
  }

  private buildRichSection(config: RichSection): FormSection {
    const section = new FormSection(
      config.id,
      { 
        type: 'flow', 
        config: {}, 
        render: this.defaultRender 
      },
      config.position
    );

    // Add the rich content with fields
    section.addElement(new RichContentSection(
      `rich-${config.id}`,
      config.content,
      config.fields,
      config.position
    ));

    return section;
  }

  private buildFieldSection(config: FieldSection): FormSection {
    console.log("Building field section:", config);
    const layout = this.createLayout(config.layout.type, config.layout.config);
    const section = new FormSection(
      config.id,
      layout,
      config.position
    );

    config.fields.forEach(fieldConfig => {
      const field = FieldFactory.createField(fieldConfig);
      console.log("Created field:", field);
      section.addElement(field);
    });

    console.log("Completed field section:", section);
    return section;
  }

  private buildTableSection(config: TableSection): FormSection {
    console.log("Building table section:", config);
    const section = new FormSection(
      config.id,
      { type: 'table', config: {}, render: this.defaultRender },
      config.position
    );

    // Create table field with columns
    const tableField = FieldFactory.createField({
      id: config.id,
      type: 'table',
      name: config.id,
      label: config.label,
      validation: {},
      options: {
        columns: config.columns,
        repeat: config.repeat
      }
    });
    
    console.log("Created table field:", tableField);
    section.addElement(tableField);

    return section;
  }

  private defaultRender = (elements: IFormElement[]): JSX.Element => {
    return React.createElement('div', {}, 
      elements.map(element => element.render())
    );
  };

  private createLayout(
    type: 'flow' | 'grid' | 'table' | 'flex',
    config: {
      columns?: number;
      gap?: number;
      spacing?: number;
      direction?: 'row' | 'column';
    }
  ): FormLayout {
    return new FormLayout(type, 'horizontal', config);
  }

  build(): Map<string, FormSection> {
    this.template.sections.forEach(sectionConfig => {
      console.log("Processing section:", sectionConfig.id);
      const section = this.buildSection(sectionConfig);
      this.sections.set(section.id, section);
    });
    console.log("Final sections:", this.sections);
    return this.sections;
  }
} 


#FormElement.ts
import { IFormElement } from '../types/form-system';

export abstract class FormElement implements IFormElement {
  constructor(
    public id: string,
    public name: string,
    public label: string,
    public type: string,
    public position: number = 0
  ) {}

  abstract render(): JSX.Element;
} 


#FormRenderer.tsx
import React from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { useMutation, useQuery } from '@apollo/client';
import { FormSection } from './FormSection';
import { FormConfig } from '../types/form';
import { createProjectInitiationTemplate } from '../templates/ProjectInitiationTemplate';
import { FormBuilder } from './FormBuilder';
import { gql } from '@apollo/client';

interface FormRendererProps {
  config: FormConfig;
}

export default function FormRenderer({ config }: FormRendererProps) {
  const methods = useForm();
  
  // Initialize form structure
  const template = createProjectInitiationTemplate({
    dept: config.dept,
    project: config.project
  });
  
  const builder = new FormBuilder(template);
  const sections = builder.build();
  const queries = template.queries;

  // Setup GraphQL queries
  const { data, loading } = useQuery(gql(queries.fetch));
  const [submitForm] = useMutation(gql(queries.submit));

  const onSubmit = async (formData: any) => {
    try {
      await submitForm({
        variables: {
          input: formData
        }
      });
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        {Array.from(sections.values())
          .sort((a, b) => a.position - b.position)
          .map((section, index) => (
            <React.Fragment key={section.id || `section-${index}`}>
              {section.render()}
            </React.Fragment>
          ))}
      </form>
    </FormProvider>
  );
} 

#FOrmSection.ts
import { IFormSection, ILayout, IFormElement } from '../types/form-system';
import { BaseContainer } from '../components/Form/core/BaseContainer';

export class FormSection extends BaseContainer implements IFormSection {
  public elements: Array<IFormElement | IFormSection> = [];
  public type: string = 'section';

  constructor(
    public id: string,
    public layout: ILayout,
    public position: number = 0
  ) {
    super();
  }

  addElement(element: IFormElement | IFormSection): void {
    this.elements.push(element);
    // Add to components for BaseContainer compatibility
    this.components.push(element);
    // Add to layout's components
    if (this.layout instanceof BaseContainer) {
      this.layout.addComponent(element);
    }
    // Sort by position if available
    this.elements.sort((a, b) => 
      ('position' in a && 'position' in b) ? a.position - b.position : 0
    );
  }

  render(): JSX.Element {
    console.log(`Rendering section ${this.id} with ${this.elements.length} elements`);
    return this.layout.render(this.elements);
  }
} 



#ProjectInitiationTemplate.ts
import { IFormTemplate } from '../types/form-system';
import React from 'react';

export const createProjectInitiationTemplate = (config: { dept: string; project: string }): IFormTemplate => ({
  id: 'project-initiation',
  name: 'Project Initiation Document',
  sections: [
     {
      id: 'header',
      type: 'rich-section',
      content: `
       <div class="section">
          <h1>Project Initiation Document</h1>
          <p>This document outlines the key aspects of project {{projectName}}.</p>
          
          <div class="project-basics">
            <h2>Project Overview</h2>
            <p>Project Name: {{projectName}}</p>
            <p>Start Date: {{startDate}}</p>
          </div>

          <div class="project-details">
            <h2>Project Details</h2>
            
          </div>
        </div>
      `,
      fields: {
        projectName: {
          id: 'project-name',
          type: 'text',
          name: 'projectName',
          label: 'Project Name',
          validation: { required: true }
        },
        startDate: {
          id: 'start-date',
          type: 'date',
          name: 'startDate',
          label: 'Start Date',
          validation: { required: true }
        }
      },
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
          label: 'Project Description',
          validation: { required: true }
        },
        {
          id: 'manager',
          type: 'text',
          name: 'manager',
          label: 'Project Manager',
          validation: { required: true }
        }
      ],
      position: 1
    }, 
    {
      id: 'resources',
      type: 'table-section',
      label: 'Resource Allocation',
      columns: [
        { field: 'name', header: 'Resource Name', type: 'text' },
        { field: 'role', header: 'Role', type: 'select',
          options: {
            items: [
              { value: 'dev', label: 'Developer' },
              { value: 'qa', label: 'QA' }
            ]
          }
        },
        { field: 'allocation', header: 'Allocation %', type: 'number' }
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
});


#App.tsx
import React, { useState } from 'react';
import { MockedProvider } from "@apollo/client/testing";
import DropDownForm from './components/DropdownForm';
import FormRenderer from './core/FormRenderer';
import { gql } from '@apollo/client';
import { FormConfig } from './types/form';

// Define the queries that match ProjectInitiationTemplate
const GET_PROJECT_DATA = gql`
  query GetProjectData($dept: String!, $project: String!) {
    projectData(dept: $dept, project: $project) {
      projectName
      startDate
      resources {
        name
        allocation
      }
    }
  }
`;

const SAVE_PROJECT_DATA = gql`
  mutation SaveProjectData($input: ProjectDataInput!) {
    saveProjectData(input: $input) {
      success
      message
    }
  }
`;

// Mock data that matches the template structure
const mocks = [
  {
    request: {
      query: GET_PROJECT_DATA,
      variables: {
        dept: "dept1",
        project: "project1"
      }
    },
    result: {
      data: {
        projectData: {
          projectName: "Sample Project",
          startDate: "2024-03-15",
          resources: [
            {
              name: "John Doe",
              allocation: 100
            },
            {
              name: "Jane Smith",
              allocation: 50
            }
          ]
        }
      }
    }
  },
  {
    request: {
      query: SAVE_PROJECT_DATA,
      variables: {
        input: {
          projectName: "Sample Project",
          startDate: "2024-03-15",
          resources: [
            {
              name: "John Doe",
              allocation: 100
            }
          ]
        }
      }
    },
    result: {
      data: {
        saveProjectData: {
          success: true,
          message: "Data saved successfully"
        }
      }
    }
  }
];

function App() {
  const [showForm, setShowForm] = useState(false);
  const [formConfig, setFormConfig] = useState<FormConfig | null>(null);

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

  return (
    <MockedProvider mocks={mocks} addTypename={false}>
      <div>
        <DropDownForm 
          onLoad={handleLoadClick} 
          isLoaded={showForm} 
        />
        {showForm && formConfig && (
          <FormRenderer config={formConfig} />
        )}
      </div>
    </MockedProvider>
  );
}

export default App;
