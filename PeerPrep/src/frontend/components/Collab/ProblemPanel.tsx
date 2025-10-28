export function ProblemPanel() {
  return (
    <div>
      <h2 className="text-2xl font-bold text-green-700 mb-3">Two Sum</h2>

      <p className="text-gray-800 text-sm mb-4">
        Given an array of integers nums and an integer target, return indices of
        the two numbers such that they add up to target. You may assume that each
        input would have exactly one solution, and you may not use the same
        element twice.
      </p>

      <h3 className="font-semibold mb-2">Example 1:</h3>
      <pre className="bg-gray-100 rounded p-2 text-sm mb-4">
        Input: nums = [2,7,11,15], target = 9{"\n"}
        Output: [0,1]
      </pre>

      <h3 className="font-semibold mb-2">Example 2:</h3>
      <pre className="bg-gray-100 rounded p-2 text-sm mb-4">
        Input: nums = [3,2,4], target = 6{"\n"}
        Output: [1,2]
      </pre>

      <h3 className="font-semibold mb-2">Constraints:</h3>
      <ul className="list-disc ml-6 text-sm text-gray-700">
        <li>2 ≤ nums.length ≤ 10⁴</li>
        <li>-10⁹ ≤ nums[i] ≤ 10⁹</li>
        <li>-10⁹ ≤ target ≤ 10⁹</li>
        <li>Only one valid answer exists.</li>
      </ul>

      <p className="mt-4 text-sm italic text-gray-600">
        Follow-up: Can you come up with an algorithm that runs in O(n)?
      </p>
    </div>
  );
}
