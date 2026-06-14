import { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid
} from 'recharts';

const API_BASE = 'http://13.219.143.181:8000';
const COLORS = ['#0d3b66', '#3a86ff', '#8338ec', '#fb5607', '#ffbe0b', '#06d6a0', '#ef476f', '#118ab2'];

function Dashboard() {
  // drill-through state: 'country' | 'department' | 'account'
  const [level, setLevel] = useState('country');
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);

  const [currency, setCurrency] = useState('usd'); // 'usd' or 'local'

  const [countryData, setCountryData] = useState([]);
  const [departmentData, setDepartmentData] = useState([]);
  const [accountData, setAccountData] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);

  const [workforce, setWorkforce] = useState([]);
  const [byCountryHC, setByCountryHC] = useState([]);
  const [variance, setVariance] = useState([]);

  const [loading, setLoading] = useState(true);

  // ── Fetch top-level data on mount ──────────────────────
  useEffect(() => {
    const fetchTopLevel = async () => {
      try {
        const [r1, r2, r3, r4] = await Promise.all([
          fetch(`${API_BASE}/financials/summary?scenario=Actual`).then(r => r.json()),
          fetch(`${API_BASE}/employees/summary`).then(r => r.json()),
          fetch(`${API_BASE}/employees/by-country`).then(r => r.json()),
          fetch(`${API_BASE}/financials/variance`).then(r => r.json()),
        ]);
        setCountryData(r1);
        setWorkforce(r2);
        setByCountryHC(r3);
        setVariance(r4);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTopLevel();
  }, []);

  // ── Drill into a country → departments ─────────────────
  const drillIntoCountry = async (country) => {
    setLoading(true);
    try {
      const data = await fetch(`${API_BASE}/financials/by-department?country=${encodeURIComponent(country)}&scenario=Actual`).then(r => r.json());
      setDepartmentData(data);
      setSelectedCountry(country);
      setLevel('department');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ── Drill into a department → accounts ─────────────────
  const drillIntoDepartment = async (department) => {
    setLoading(true);
    try {
      const data = await fetch(`${API_BASE}/financials/by-account?country=${encodeURIComponent(selectedCountry)}&department=${encodeURIComponent(department)}&scenario=Actual`).then(r => r.json());
      setAccountData(data);
      setSelectedDepartment(department);
      setLevel('account');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ── Drill into an account → monthly trend ───────────────
  const drillIntoAccount = async (accountCode, accountName) => {
    setLoading(true);
    try {
      const data = await fetch(`${API_BASE}/financials/monthly?country=${encodeURIComponent(selectedCountry)}&department=${encodeURIComponent(selectedDepartment)}&account_code=${encodeURIComponent(accountCode)}&scenario=Actual`).then(r => r.json());
      setMonthlyData(data);
      setSelectedAccount(accountName);
      setLevel('monthly');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ── Back navigation ──────────────────────────────────────
  const goBack = () => {
    if (level === 'monthly') {
      setLevel('account');
      setSelectedAccount(null);
    } else if (level === 'account') {
      setLevel('department');
      setSelectedDepartment(null);
    } else if (level === 'department') {
      setLevel('country');
      setSelectedCountry(null);
    }
  };

  const fmtMoney = (v) => `$${(Number(v)/1e6).toFixed(1)}M`;
  const fmtMoneyFull = (v, curr = 'USD') => `${Number(v).toLocaleString(undefined, {maximumFractionDigits: 0})} ${curr}`;

  if (loading) return <div className="dashboard-loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">

      {/* Breadcrumb / Back button */}
      {level !== 'country' && (
        <div className="breadcrumb">
          <button className="back-btn" onClick={goBack}>← Back</button>
          <span className="breadcrumb-path">
            {selectedCountry}
            {selectedDepartment && ` / ${selectedDepartment}`}
            {selectedAccount && ` / ${selectedAccount}`}
          </span>
        </div>
      )}

      {/* ───────────── LEVEL 1: Country ───────────── */}
      {level === 'country' && (
        <>
          <div className="dash-section">
            <h2>💰 P&L Overview by Country (Actuals, USD)</h2>
            <p className="hint">Click a bar to drill into department-level detail</p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={countryData} onClick={(e) => {
                if (e && e.activePayload && e.activePayload[0]) {
                  drillIntoCountry(e.activePayload[0].payload.country);
                }
              }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis tickFormatter={fmtMoney} width={70} />
                <Tooltip formatter={(v) => fmtMoney(v)} />
                <Legend />
                <Bar dataKey="total_revenue" fill="#0d3b66" name="Revenue" cursor="pointer" />
                <Bar dataKey="total_expenses" fill="#fb5607" name="Expenses" cursor="pointer" />
                <Bar dataKey="net_profit" fill="#06d6a0" name="Net Profit" cursor="pointer" />
              </BarChart>
            </ResponsiveContainer>
            <table className="dash-table">
              <thead>
                <tr><th>Country</th><th>Currency</th><th>Revenue</th><th>Expenses</th><th>Net Profit</th><th></th></tr>
              </thead>
              <tbody>
                {countryData.map((row, i) => (
                  <tr key={i} className="clickable-row" onClick={() => drillIntoCountry(row.country)}>
                    <td>{row.country}</td>
                    <td>{row.currency}</td>
                    <td>{fmtMoney(row.total_revenue)}</td>
                    <td>{fmtMoney(row.total_expenses)}</td>
                    <td>{fmtMoney(row.net_profit)}</td>
                    <td>→</td>
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
            <h2>📈 Forecast vs Budget Variance by Country (2025-2026)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={variance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis tickFormatter={fmtMoney} width={70} />
                <Tooltip formatter={(v) => fmtMoney(v)} />
                <Legend />
                <Bar dataKey="variance_revenue" fill="#06d6a0" name="Revenue Variance" />
                <Bar dataKey="variance_profit" fill="#ef476f" name="Profit Variance" />
              </BarChart>
            </ResponsiveContainer>
            <table className="dash-table">
              <thead>
                <tr><th>Country</th><th>Budget Revenue</th><th>Forecast Revenue</th><th>Revenue Variance</th><th>Profit Variance</th></tr>
              </thead>
              <tbody>
                {variance.map((row, i) => (
                  <tr key={i}>
                    <td>{row.country}</td>
                    <td>{fmtMoney(row.budget_revenue)}</td>
                    <td>{fmtMoney(row.forecast_revenue)}</td>
                    <td>{fmtMoney(row.variance_revenue)}</td>
                    <td>{fmtMoney(row.variance_profit)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* ───────────── LEVEL 2: Department ───────────── */}
      {level === 'department' && (
        <div className="dash-section">
          <h2>🏢 {selectedCountry} — P&L by Department (USD)</h2>
          <p className="hint">Click a bar or row to drill into account-level detail</p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={departmentData} onClick={(e) => {
              if (e && e.activePayload && e.activePayload[0]) {
                drillIntoDepartment(e.activePayload[0].payload.department_name);
              }
            }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department_name" angle={-20} textAnchor="end" height={90} fontSize={11} />
              <YAxis tickFormatter={fmtMoney} width={70} />
              <Tooltip formatter={(v) => fmtMoney(v)} />
              <Legend />
              <Bar dataKey="total_revenue" fill="#0d3b66" name="Revenue" cursor="pointer" />
              <Bar dataKey="total_expenses" fill="#fb5607" name="Expenses" cursor="pointer" />
              <Bar dataKey="net_profit" fill="#06d6a0" name="Net Profit" cursor="pointer" />
            </BarChart>
          </ResponsiveContainer>
          <table className="dash-table">
            <thead>
              <tr><th>Department</th><th>Revenue</th><th>Expenses</th><th>Net Profit</th><th></th></tr>
            </thead>
            <tbody>
              {departmentData.map((row, i) => (
                <tr key={i} className="clickable-row" onClick={() => drillIntoDepartment(row.department_name)}>
                  <td>{row.department_name}</td>
                  <td>{fmtMoney(row.total_revenue)}</td>
                  <td>{fmtMoney(row.total_expenses)}</td>
                  <td>{fmtMoney(row.net_profit)}</td>
                  <td>→</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ───────────── LEVEL 3: Account (Chart of Accounts) ───────────── */}
      {level === 'account' && (
        <div className="dash-section">
          <h2>📋 {selectedCountry} / {selectedDepartment} — Chart of Accounts (USD)</h2>
          <p className="hint">Click a row to see the monthly trend for that account</p>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={accountData} layout="vertical" margin={{ left: 60 }} onClick={(e) => {
              if (e && e.activePayload && e.activePayload[0]) {
                const row = e.activePayload[0].payload;
                drillIntoAccount(row.account_code, row.account_name);
              }
            }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={fmtMoney} />
              <YAxis type="category" dataKey="account_name" width={180} fontSize={11} />
              <Tooltip formatter={(v) => fmtMoney(v)} />
              <Bar dataKey="total_amount_usd" name="Amount" cursor="pointer">
                {accountData.map((entry, i) => (
                  <Cell key={i} fill={entry.account_type === 'Revenue' ? '#06d6a0' : '#fb5607'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <table className="dash-table">
            <thead>
              <tr><th>Code</th><th>Account</th><th>Group</th><th>Category</th><th>Type</th><th>Amount (USD)</th><th></th></tr>
            </thead>
            <tbody>
              {accountData.map((row, i) => (
                <tr key={i} className="clickable-row" onClick={() => drillIntoAccount(row.account_code, row.account_name)}>
                  <td>{row.account_code}</td>
                  <td>{row.account_name}</td>
                  <td>{row.account_group}</td>
                  <td>{row.account_category}</td>
                  <td>{row.account_type}</td>
                  <td>{fmtMoney(row.total_amount_usd)}</td>
                  <td>→</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ───────────── LEVEL 4: Monthly Trend ───────────── */}
      {level === 'monthly' && (
        <div className="dash-section">
          <div className="currency-toggle">
            <h2>📅 {selectedCountry} / {selectedDepartment} / {selectedAccount} — Monthly Trend</h2>
            <div className="toggle-buttons">
              <button className={currency === 'usd' ? 'toggle-btn active' : 'toggle-btn'} onClick={() => setCurrency('usd')}>USD</button>
              <button className={currency === 'local' ? 'toggle-btn active' : 'toggle-btn'} onClick={() => setCurrency('local')}>
                Local {monthlyData[0]?.currency ? `(${monthlyData[0].currency})` : ''}
              </button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period_date" fontSize={11} />
              <YAxis tickFormatter={(v) => `${(v/1e6).toFixed(1)}M`} width={70} />
              <Tooltip formatter={(v) => fmtMoneyFull(v, currency === 'usd' ? 'USD' : (monthlyData[0]?.currency || ''))} />
              <Legend />
              <Line
                type="monotone"
                dataKey={currency === 'usd' ? 'amount_usd' : 'amount_local'}
                stroke="#0d3b66"
                name={`Amount (${currency === 'usd' ? 'USD' : (monthlyData[0]?.currency || 'Local')})`}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
          <table className="dash-table">
            <thead>
              <tr><th>Month</th><th>Amount (USD)</th><th>Amount (Local)</th><th>Currency</th></tr>
            </thead>
            <tbody>
              {monthlyData.map((row, i) => (
                <tr key={i}>
                  <td>{row.period_date}</td>
                  <td>{fmtMoneyFull(row.amount_usd, 'USD')}</td>
                  <td>{fmtMoneyFull(row.amount_local, row.currency)}</td>
                  <td>{row.currency}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}

export default Dashboard;
