/**
 * Selector for choosing summary generation type.
 */

import { SummaryType } from '@/types/summary';

interface SummaryTypeSelectorProps {
  value: SummaryType;
  onChange: (value: SummaryType) => void;
  disabled?: boolean;
}

const summaryTypeOptions: Array<{ value: SummaryType; label: string; description: string }> = [
  {
    value: 'brief',
    label: 'Brief',
    description: '2-3 sentence overview',
  },
  {
    value: 'detailed',
    label: 'Detailed',
    description: 'Comprehensive multi-paragraph summary',
  },
  {
    value: 'bullet_points',
    label: 'Bullet Points',
    description: 'Key takeaways in list format',
  },
];

export function SummaryTypeSelector({
  value,
  onChange,
  disabled = false,
}: SummaryTypeSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
        Summary Type
      </label>
      <div className="grid sm:grid-cols-3 gap-2">
        {summaryTypeOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            disabled={disabled}
            onClick={() => onChange(option.value)}
            className={`text-left p-3 border rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
              value === option.value
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-900 dark:text-blue-100'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
          >
            <div className="font-medium text-sm">{option.label}</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{option.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
