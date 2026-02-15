import React, { useState, useEffect } from 'react';
import {
    IonContent, IonPage, IonIcon, IonToast, IonLoading
} from '@ionic/react';
import {
    medkitOutline,
    eyeOutline,
    eyeOffOutline,
    mailOutline,
    lockClosedOutline,
    personOutline,
    arrowForward
} from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import api from '../api';
import medicyLogo from '../assets/medicy_logo.png';
import './Auth.css';

const Auth: React.FC = () => {
    const history = useHistory();
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    // Form State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [role, setRole] = useState('Recipient');
    const [departmentId, setDepartmentId] = useState('');

    const [departments, setDepartments] = useState<any[]>([]);

    useEffect(() => {
        // Load departments for doctor signup
        const fetchDepts = async () => {
            try {
                const res = await api.get('/departments');
                setDepartments(res.data);
            } catch (err) {
                console.error("Failed to load departments", err);
            }
        };
        fetchDepts();
    }, []);

    const handleAuth = async () => {
        if (!email || !password) {
            setToastMessage('Please enter email and password');
            setShowToast(true);
            return;
        }

        if (!isLogin && !fullName) {
            setToastMessage('Please enter your full name');
            setShowToast(true);
            return;
        }

        setLoading(true);
        try {
            if (isLogin) {
                // Login
                const payload = {
                    email: email,
                    password: password
                };

                const res = await api.post('/auth/login', payload);
                const { access_token, role, doctor_id } = res.data;

                localStorage.setItem('token', access_token);
                localStorage.setItem('role', role); // Backend returns 'role'
                localStorage.setItem('email', email);
                if (doctor_id) localStorage.setItem('doctor_id', doctor_id.toString());

                // Redirect based on role
                switch (role) {
                    case 'Admin': history.push('/admin-dashboard'); break;
                    case 'Doctor': history.push('/doctor-dashboard'); break;
                    case 'Recipient': history.push('/recipient-dashboard'); break;
                    case 'Patient': history.push('/patient-dashboard'); break;
                    default: history.push('/dashboard');
                }
            } else {
                // Register
                const payload: any = {
                    email,
                    password,
                    full_name: fullName,
                    role
                };

                if (role === 'Doctor') {
                    if (!departmentId) {
                        setToastMessage('Doctors must select a department');
                        setShowToast(true);
                        setLoading(false);
                        return;
                    }
                    payload.department_id = departmentId; // Send as string (UUID)
                }

                await api.post('/auth/register', payload);
                setToastMessage('Registration successful! Please login.');
                setShowToast(true);
                setIsLogin(true); // Switch to login
            }
        } catch (err: any) {
            console.error(err);
            const msg = err.response?.data?.detail || 'Authentication failed';
            setToastMessage(msg);
            setShowToast(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <IonPage className="auth-page-split">
            <IonContent fullscreen>
                <div className="split-layout">
                    {/* Left Side: Branding & Illustration */}
                    <div className="auth-banner">
                        <div className="banner-content">
                            <div className="logo-brand">
                                <img src={medicyLogo} alt="Medicy" className="brand-logo-img-auth" />
                                <span>Medicy</span>
                            </div>
                            <h1>Healthcare<br />Reimagined.</h1>
                            <p>
                                Join the world's most advanced AI-powered patient triage system.
                                Efficient, Accurate, and Life-saving.
                            </p>
                            <div className="glass-stats">
                                <div className="stat">
                                    <strong>10k+</strong>
                                    <span>Patients</span>
                                </div>
                                <div className="stat">
                                    <strong>99%</strong>
                                    <span>Accuracy</span>
                                </div>
                                <div className="stat">
                                    <strong>24/7</strong>
                                    <span>Support</span>
                                </div>
                            </div>
                        </div>
                        {/* Decorative Circles */}
                        <div className="circle circle-1"></div>
                        <div className="circle circle-2"></div>
                    </div>

                    {/* Right Side: Form */}
                    <div className="auth-form-container">
                        <div className="form-wrapper">
                            <div className="form-header">
                                <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
                                <p>{isLogin ? 'Enter your details to access your account' : 'Get started with your free account today'}</p>
                            </div>

                            {/* Custom Toggle */}
                            <div className="auth-toggle">
                                <button
                                    className={`toggle-btn ${isLogin ? 'active' : ''}`}
                                    onClick={() => setIsLogin(true)}
                                >
                                    Login
                                </button>
                                <button
                                    className={`toggle-btn ${!isLogin ? 'active' : ''}`}
                                    onClick={() => setIsLogin(false)}
                                >
                                    Sign Up
                                </button>
                            </div>

                            <form className="modern-form" onSubmit={(e) => { e.preventDefault(); handleAuth(); }}>

                                {!isLogin && (
                                    <div className="input-group">
                                        <label>Full Name</label>
                                        <div className="input-field">
                                            <IonIcon icon={personOutline} />
                                            <input
                                                type="text"
                                                placeholder="John Doe"
                                                value={fullName}
                                                onChange={e => setFullName(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                )}

                                <div className="input-group">
                                    <label>Email Address</label>
                                    <div className="input-field">
                                        <IonIcon icon={mailOutline} />
                                        <input
                                            type="email"
                                            placeholder="name@hospital.com"
                                            value={email}
                                            onChange={e => setEmail(e.target.value)}
                                        />
                                    </div>
                                </div>

                                <div className="input-group">
                                    <label>Password</label>
                                    <div className="input-field">
                                        <IonIcon icon={lockClosedOutline} />
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            placeholder="••••••••"
                                            value={password}
                                            onChange={e => setPassword(e.target.value)}
                                        />
                                        <IonIcon
                                            icon={showPassword ? eyeOffOutline : eyeOutline}
                                            className="toggle-password"
                                            onClick={() => setShowPassword(!showPassword)}
                                        />
                                    </div>
                                </div>

                                {!isLogin && (
                                    <>
                                        <div className="input-group">
                                            <label>Role</label>
                                            <div className="input-field select-field">
                                                <select value={role} onChange={e => setRole(e.target.value)}>
                                                    <option value="Recipient">Triage Officer</option>
                                                    <option value="Doctor">Doctor</option>
                                                    <option value="Admin">Administrator</option>
                                                    <option value="Patient">Patient</option>
                                                </select>
                                            </div>
                                        </div>

                                        {role === 'Doctor' && (
                                            <div className="input-group">
                                                <label>Department</label>
                                                <div className="input-field select-field">
                                                    <select value={departmentId} onChange={e => setDepartmentId(e.target.value)}>
                                                        <option value="">Select Department</option>
                                                        {departments.map(dept => (
                                                            <option key={dept.department_id} value={dept.department_id}>
                                                                {dept.name}
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}

                                <button type="submit" className="submit-btn" disabled={loading}>
                                    {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                                    {!loading && <IonIcon icon={arrowForward} />}
                                </button>
                            </form>

                            <div className="form-footer">
                                <p>
                                    {isLogin ? "Don't have an account? " : "Already have an account? "}
                                    <span onClick={() => setIsLogin(!isLogin)}>
                                        {isLogin ? 'Sign Up' : 'Log In'}
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <IonLoading isOpen={loading} message="Authenticating..." />
                <IonToast
                    isOpen={showToast}
                    onDidDismiss={() => setShowToast(false)}
                    message={toastMessage}
                    duration={2000}
                    color="danger"
                    position="top"
                />
            </IonContent>
        </IonPage>
    );
};

export default Auth;
