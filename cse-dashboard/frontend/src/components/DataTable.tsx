interface Column<T> {
  key: keyof T;
  label: string;
  render?: (row: T) => React.ReactNode;
}

interface Props<T> {
  data: T[];
  columns: Column<T>[];
}

export default function DataTable<T>({ data, columns }: Props<T>) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.key)}
                scope="col"
                className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-600"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-slate-50">
              {columns.map((col) => (
                <td key={String(col.key)} className="whitespace-nowrap px-3 py-2 text-sm text-slate-700">
                  {col.render ? col.render(row) : String(row[col.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
