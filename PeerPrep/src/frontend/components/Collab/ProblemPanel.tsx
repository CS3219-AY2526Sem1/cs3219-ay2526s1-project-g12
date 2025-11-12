type ProblemPanelProps = {
  title: string;
  description: string;
};

export function ProblemPanel({ title, description }: ProblemPanelProps) {
  return (
    <>
      <h2 className="text-4xl font-semibold mb-3">{title}</h2>

      <p className="mb-4 whitespace-pre-line">{description}</p>
    </>
  );
}
