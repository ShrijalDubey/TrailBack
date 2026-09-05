import {Outlet} from 'react-router-dom';import Sidebar from './Sidebar';import Topbar from './Topbar';import {useAuth} from '../../context/AuthContext';
export default function AppShell(){const {logout}=useAuth();return <div className="app-shell"><Sidebar logout={logout}/><div className="main"><Topbar/><main className="content"><Outlet/></main></div></div>}
