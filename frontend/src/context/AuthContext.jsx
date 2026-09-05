import {createContext,useContext,useEffect,useState} from 'react';
import {api} from '../api/client';
const C=createContext(null);
export function AuthProvider({children}){const [session,setSession]=useState(()=>JSON.parse(localStorage.getItem('trailback_session')||'null')); const [loading,setLoading]=useState(!!localStorage.getItem('trailback_api_key'));
 useEffect(()=>{if(!loading)return; api.me().then(r=>{setSession(r.data);localStorage.setItem('trailback_session',JSON.stringify(r.data));}).catch(()=>{localStorage.removeItem('trailback_api_key');localStorage.removeItem('trailback_session');setSession(null)}).finally(()=>setLoading(false))},[]);
 const login=async(key)=>{localStorage.setItem('trailback_api_key',key.trim());const r=await api.me();setSession(r.data);localStorage.setItem('trailback_session',JSON.stringify(r.data));}; const logout=()=>{localStorage.removeItem('trailback_api_key');localStorage.removeItem('trailback_session');setSession(null)}; return <C.Provider value={{session,loading,login,logout}}>{children}</C.Provider>}
export const useAuth=()=>useContext(C);
