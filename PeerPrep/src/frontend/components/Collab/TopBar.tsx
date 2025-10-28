export function TopBar() {
  return (
    <div className="flex justify-between items-center bg-white shadow-sm p-4 border-b">
      <h1 className="text-3xl font-semibold text-green-700">
        PeerPrep <span className="text-gray-800 font-normal">Two Sum</span>
      </h1>

      <div className="flex gap-4 items-center">
        <div className="flex flex-col bg-gray-100 px-4 py-2 rounded-xl text-center">
          <span className="text-sm text-gray-600">Time Elapsed</span>
          <span className="text-xl font-semibold">8m 45s</span>
          <span className="text-xs text-gray-500">Array | Easy</span>
        </div>

        <div className="bg-gray-100 px-4 py-2 rounded-xl text-center">
          <span className="text-sm text-gray-600 block">
            Your matched partner
          </span>
          <div className="text-lg font-semibold">Gavin Sin</div>
          <div className="text-xs text-green-600 font-medium">CONNECTED</div>
        </div>

        <div className="flex gap-2">
          <button className="bg-red-400 text-white px-3 py-2 rounded-lg">
            Exit
          </button>
          <button className="bg-blue-800 text-white px-3 py-2 rounded-lg">
            Switch
          </button>
        </div>
      </div>
    </div>
  );
};
