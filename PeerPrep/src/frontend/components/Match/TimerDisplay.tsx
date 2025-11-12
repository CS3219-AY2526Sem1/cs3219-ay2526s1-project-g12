export function TimerDisplay({
  minutes,
  seconds,
}: {
  minutes: string;
  seconds: string;
}) {
  return (
    <>
      <div className="bg-success px-6 py-3 rounded">
        <div className="text-2xl font-semibold">{minutes}</div>
        <div className="text-sm">minutes</div>
      </div>
      <div className="bg-success px-6 py-3 rounded">
        <div className="text-2xl font-semibold">{seconds}</div>
        <div className="text-sm">sec</div>
      </div>
    </>
  );
}
