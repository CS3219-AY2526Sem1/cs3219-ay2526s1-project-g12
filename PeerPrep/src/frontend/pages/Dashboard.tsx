import NavBar from '../components/NavBar';
import { NAV_BUTTONS } from '../config/NavConfig';
import { useAuth } from '../context/AuthContext';

function Dashboard() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen px-20 py-10">
      <NavBar buttons={NAV_BUTTONS} />

      {/* Welcome Section */}
      <h1 className="text-6xl font-semibold p-2">
        Welcome, {user?.first_name} {user?.last_name}
      </h1>
      <p className="text-2xl p-2 font-light tracking-widest">For your review</p>
      <div className="flex p-2 gap-6">
        <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
          <div className="card-body p-4 gap-0.5">
            <h2 className="font-medium text-base">Total Interviews Done</h2>
            <h2 className="font-extrabold text-4xl">40</h2>
            <p className="font-medium">013 Easy | 020 Medium | 007 Hard</p>
          </div>
        </div>

        <div className="card w-72 card-xs shadow-sm border-1 border-base-200">
          <div className="card-body p-4 gap-0.5">
            <h2 className="font-medium text-base">Total Time Spent</h2>
            <h2 className="font-extrabold text-4xl">4h 12m</h2>
          </div>
        </div>
      </div>

      {/* Recent Matches Table */}
      <p className="text-2xl p-2 font-light tracking-widest">
        Your recent matches
      </p>
      <div className="overflow-x-auto rounded-box shadow-sm border-1 border-base-200">
        <table className="table">
          {/* Table Head */}
          <thead>
            <tr>
              <th></th>
              <th>Question</th>
              <th>Category</th>
              <th>Difficulty</th>
              <th>Time Elapsed</th>
              <th>Partner</th>
            </tr>
          </thead>

          {/* Table Body */}
          <tbody>
            <tr>
              <td className="font-semibold">1</td>
              <td className="font-semibold">Two Sum</td>
              <td className="font-semibold">Array</td>
              <td className="font-semibold">Easy</td>
              <td>30min</td>
              <td>Bryce Ang Hong Jun</td>
            </tr>
            <tr>
              <td className="font-semibold">2</td>
              <td className="font-semibold">3 Sum</td>
              <td className="font-semibold">Array</td>
              <td className="font-semibold">Medium</td>
              <td>45min</td>
              <td>Bryce Ang Hong Jun</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;
