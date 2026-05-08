export interface LabelSize {
  value: string
  label: string
  width: number
  height: number
  orientation: 'portrait' | 'landscape'
}

export const LABEL_SIZES: readonly LabelSize[] = [
  {
    value: '4x3',
    label: '4" x 3" (101.6 x 76.2mm) Horizontal',
    width: 101.6,
    height: 76.2,
    orientation: 'landscape',
  },
  {
    value: '3x4',
    label: '3" x 4" (76.2 x 101.6mm) Vertical',
    width: 76.2,
    height: 101.6,
    orientation: 'portrait',
  },
  {
    value: '2x4',
    label: '2" x 4" (57.15 x 101.6mm) Vertical',
    width: 57.15,
    height: 101.6,
    orientation: 'portrait',
  },
  {
    value: '4x2',
    label: '4" x 2" (101.6 x 57.15mm) Horizontal',
    width: 101.6,
    height: 57.15,
    orientation: 'landscape',
  },
] as const