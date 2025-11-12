import * as React from 'react';

/**
 * Converts a string to a HEX color code.
 *
 * @param {string} string - The string to convert
 * @returns {string} The HEX color code
 */
export function stringToColor(string: string): string {
  let hash = 0;
  let i;

  for (i = 0; i < string.length; i += 1) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }

  let color = '#';

  for (i = 0; i < 3; i += 1) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }

  return color;
}

type Props = {
  name: string;
};

/**
 * A clickable chip with category name.
 *
 * @param {string} name - Name of the category
 * @returns {React.FunctionComponent} The category chip
 */
const CategoryChip: React.FC<Props> = ({ name }) => {
  return (
    <div
      className="badge"
      style={{
        backgroundColor: stringToColor(name),
        color: '#fff',
      }}
    >
      {name}
    </div>
  );
};

export default CategoryChip;
