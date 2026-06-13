import { useState, useEffect } from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid
} from 'recharts';

const API_BASE = 'http://localhost:8000';
const COLORS = ['#0d3b66', '#3a86ff', '#8338ec', '#fb5607', '#ffbe0b', '#06d6a0', '#ef476f', '#118ab2'];

function Dashboard() {
  const [pnlByCountry, setPnlByCountry] = useState([]);
  
  const [workforce, setWorkforce] = useState([]);
  const [byCountryHC, setByCountryHC] = useState([]);
  const [variance, setVariance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [r1, r2, r3, r4, r5] = await Promise.all([
          fetch(`${API_BASE}/pnl/actual/by-country`).then(r => r.json()),
          fetch(`${API_BASE}/pnl/actual/summary`).then(r => r.json()),
          fetch(`${API_BASE}/employees/summary`).then(r => r.json()),
          fetch(`${API_BASE}/employees/by-country`).then(r => r.json()),
          fetch(`${API_BASE}/pnl/variance`).then(r => r.json()),
        ]);
        setPnlByCountry(r1);
        
        setWorkforce(r3);
        setByCountryHC(r4);
        setVariance(r5);
      
       } catch (err) {
        console.error(err);
        
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  if (loading) return <div className="dashboard-loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">


      
      {/* P&L by Country */}
      <div className="dash-section">
        <h2>💰 P&L Overview by Country</h2>
        <div className="dash-row">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={pnlByCountry}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="country" />
              <YAxis tickFormatter={(v) => `$${(v/1e6).toFixed(0)}M`} />
              <Tooltip formatter={(v) => `$${(v/1e6).toFixed(1)}M`} />
              <Legend />
              <Bar dataKey="total_revenue" fill="#0d3b66" name="Revenue" />
              <Bar dataKey="total_expenses" fill="#fb5607" name="Expenses" />
              <Bar dataKey="total_net_profit" fill="#06d6a0" name="Net Profit" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <table className="dash-table">
          <thead>
            <tr><th>Country</th><th>Revenue</th><th>Expenses</th><th>Net Profit</th></tr>
          </thead>
          <tbody>
            {pnlByCountry.map((row, i) => (
              <tr key={i}>
                <td>{row.country}</td>
                <td>${(row.total_revenue/1e6).toFixed(1)}M</td>
                <td>${(row.total_expenses/1e6).toFixed(1)}M</td>
                <td>${(row.total_net_profit/1e6).toFixed(1)}M</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Workforce */}
      <div className="dash-section">
        <h2>👥 Workforce Overview by Department</h2>
        <div className="dash-row">
          <ResponsiveContainer width="50%" height={300}>
            <PieChart>
              <Pie
                data={workforce}
                dataKey="headcount"
                nameKey="department"
                cx="50%" cy="50%"
                outerRadius={100}
                label={(entry) => entry.department}
              >
                {workforce.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <ResponsiveContainer width="50%" height={300}>
            <BarChart data={workforce}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" angle={-20} textAnchor="end" height={80} fontSize={11} />
              <YAxis />
              <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
              <Bar dataKey="avg_salary" fill="#3a86ff" name="Avg Salary" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <table className="dash-table">
          <thead>
            <tr><th>Department</th><th>Headcount</th><th>Avg Salary</th><th>Avg Total Comp</th></tr>
          </thead>
          <tbody>
            {workforce.map((row, i) => (
              <tr key={i}>
                <td>{row.department}</td>
                <td>{row.headcount}</td>
                <td>${Number(row.avg_salary).toLocaleString()}</td>
                <td>${Number(row.avg_total_comp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Headcount by Country */}
      <div className="dash-section">
        <h2>🌍 Headcount by Country</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={byCountryHC}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="country" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="headcount" fill="#8338ec" name="Headcount" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Budget Variance */}
      <div className="dash-section">
        <h2>📈 Budget vs Actual Variance by Country</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={variance}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="country" />
            <YAxis tickFormatter={(v) => `$${(v/1e6).toFixed(1)}M`} width={80} />
            <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
            <Legend />
            <Bar dataKey="total_variance_revenue" fill="#06d6a0" name="Revenue Variance" />
            <Bar dataKey="total_variance_profit" fill="#ef476f" name="Profit Variance" />
          </BarChart>
        </ResponsiveContainer>
        <table className="dash-table">
          <thead>
            <tr><th>Country</th><th>Revenue Variance</th><th>Expense Variance</th><th>Profit Variance</th></tr>
          </thead>
          <tbody>
            {variance.map((row, i) => (
              <tr key={i}>
                <td>{row.country}</td>
                <td>${Number(row.total_variance_revenue).toLocaleString()}</td>
                <td>${Number(row.total_variance_expenses).toLocaleString()}</td>
                <td>${Number(row.total_variance_profit).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default Dashboard;
