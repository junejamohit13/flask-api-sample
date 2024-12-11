import React from 'react';
import { Grid } from '@mui/material';
import { BaseContainer } from '../core/BaseContainer';
import { ILayout, IFormElement } from '../../../types/form-system';

interface LayoutConfig {
  columns?: number;
  gap?: number;
  spacing?: number;
  direction?: 'row' | 'column';
}

export class FormLayout extends BaseContainer implements ILayout {
  public id: string = '';
  public position: number = 0;

  constructor(
    public type: 'flow' | 'grid' | 'table' | 'flex',
    public orientation: 'horizontal' | 'vertical',
    public config: LayoutConfig = {}
  ) {
    super();
  }

  private getGridSize(): number {
    switch (this.type) {
      case 'flow': return 12;
      case 'grid': return this.config.columns ? 12 / this.config.columns : 6;
      case 'table': return 12;
      case 'flex': return 12;
      default: return 12;
    }
  }

  render(): JSX.Element {
    console.log("Layout rendering with components:", this.components);
    return (
      <Grid 
        container 
        spacing={this.config.spacing || 2} 
        direction={this.orientation === 'horizontal' ? 'row' : 'column'}
      >
        {this.components.map((component, index) => {
          console.log(`Rendering component ${index}:`, component);
          return (
            <Grid 
              item 
              xs={12} 
              md={this.getGridSize()} 
              key={`${component.id}-${index}`}
              sx={{ gap: this.config.gap }}
            >
              {component.render()}
            </Grid>
          );
        })}
      </Grid>
    );
  }
} 

###FOrmlayouts.tsx
import React from 'react';
import { Grid } from '@mui/material';
import { BaseContainer } from '../core/BaseContainer';
import { ILayout, IFormElement } from '../../../types/form-system';

interface LayoutConfig {
  columns?: number;
  gap?: number;
  spacing?: number;
  direction?: 'row' | 'column';
}

export class FormLayout extends BaseContainer implements ILayout {
  public id: string = '';
  public position: number = 0;

  constructor(
    public type: 'flow' | 'grid' | 'table' | 'flex',
    public orientation: 'horizontal' | 'vertical',
    public config: LayoutConfig = {}
  ) {
    super();
  }

  private getGridSize(): number {
    switch (this.type) {
      case 'flow': return 12;
      case 'grid': return this.config.columns ? 12 / this.config.columns : 6;
      case 'table': return 12;
      case 'flex': return 12;
      default: return 12;
    }
  }

  render(): JSX.Element {
    console.log("Layout rendering with components:", this.components);
    return (
      <Grid 
        container 
        spacing={this.config.spacing || 2} 
        direction={this.orientation === 'horizontal' ? 'row' : 'column'}
      >
        {this.components.map((component, index) => {
          console.log(`Rendering component ${index}:`, component);
          return (
            <Grid 
              item 
              xs={12} 
              md={this.getGridSize()} 
              key={`${component.id}-${index}`}
              sx={{ gap: this.config.gap }}
            >
              {component.render()}
            </Grid>
          );
        })}
      </Grid>
    );
  }
} 

##DIsplayvalue.tsx
import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface DisplayValuesProps {
  formData: {
    primaryFormData: {
      dept: string;
      employee: string;
      office: string;
    };
    secondaryFormData: {
      project: string;
      task: string;
    };
  };
}

export default function DisplayValues({ formData }: DisplayValuesProps) {
  return (
    <Box sx={{ m: 2 }}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Selected Values
          </Typography>
          
          <Typography variant="subtitle1" gutterBottom>
            Primary Information:
          </Typography>
          <Typography>Department: {formData.primaryFormData.dept}</Typography>
          <Typography>Employee: {formData.primaryFormData.employee}</Typography>
          <Typography>Office: {formData.primaryFormData.office}</Typography>

          <Typography variant="subtitle1" sx={{ mt: 2 }} gutterBottom>
            Project Details:
          </Typography>
          <Typography>Project: {formData.secondaryFormData.project}</Typography>
          <Typography>Task: {formData.secondaryFormData.task}</Typography>
        </CardContent>
      </Card>
    </Box>
  );
} 
