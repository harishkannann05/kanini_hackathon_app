import React, { useEffect, useState } from 'react';
import {
    IonContent, IonPage, IonCard, IonCardHeader, IonCardTitle, IonCardContent,
    IonItem, IonLabel, IonInput, IonButton, IonSegment, IonSegmentButton,
    IonSelect, IonSelectOption, IonToast, IonLoading
} from '@ionic/react';
import { useHistory } from 'react-router-dom';
import api from '../api';
import './Auth.css'; // We will create this CSS file next

const Auth: React.FC = () => {
    const history = useHistory();
    const [mode, setMode] = useState<'login' | 'signup'>('login');
    const [loading, setLoading] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    // Form State
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [role, setRole] = useState('Patient');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [age, setAge] = useState('');
    const [gender, setGender] = useState('Male');
    const [departmentId, setDepartmentId] = useState('');
    const [specialization, setSpecialization] = useState('');
    const [experienceYears, setExperienceYears] = useState('');
    const [departments, setDepartments] = useState<Array<{ department_id: string; name: string }>>([]);

    useEffect(() => {
        const loadDepartments = async () => {
            try {
                const res = await api.get('/departments');
                setDepartments(res.data || []);
            } catch (err) {
                console.error('Failed to load departments', err);
            }
        };
        loadDepartments();
    }, []);

    const handleAuth = async () => {
        if (mode === 'signup') {
            if (!fullName.trim()) {
                setToastMessage('Full name is required.');
                setShowToast(true);
                return;
            }
            if (!email.trim() || !password.trim()) {
                setToastMessage('Email and password are required.');
                setShowToast(true);
                return;
            }
            if (role === 'Patient' && (!age || !phoneNumber.trim())) {
                setToastMessage('Phone number and age are required for patients.');
                setShowToast(true);
                return;
            }
            if (role === 'Doctor' && !departmentId) {
                setToastMessage('Doctor must select a department.');
                setShowToast(true);
                return;
            }
        } else {
            if (!email.trim() || !password.trim()) {
                setToastMessage('Email and password are required.');
                setShowToast(true);
                return;
            }
        }

        setLoading(true);
        try {
            let response;
            if (mode === 'signup') {
                response = await api.post('/auth/register', {
                    email,
                    password,
                    full_name: fullName,
                    role,
                    phone_number: phoneNumber || undefined,
                    age: age ? parseInt(age, 10) : undefined,
                    gender: role === 'Patient' ? gender : undefined,
                    department_id: role === 'Doctor' ? departmentId : undefined,
                    specialization: role === 'Doctor' ? specialization : undefined,
                    experience_years: role === 'Doctor' && experienceYears ? parseInt(experienceYears, 10) : undefined
                });
                setToastMessage("Account created! Please login.");
                setShowToast(true);
                setMode('login'); // Switch to login after signup
            } else {
                response = await api.post('/auth/login', {
                    email,
                    password
                });
                const { access_token, role: userRole, doctor_id, user_id } = response.data;
                localStorage.setItem('token', access_token);
                localStorage.setItem('role', userRole);
                if (doctor_id) localStorage.setItem('doctor_id', doctor_id);
                if (user_id) localStorage.setItem('user_id', user_id);

                // Redirect logic
                switch (userRole) {
                    case 'Admin': history.push('/admin-dashboard'); break; // Admin Dashboard
                    case 'Doctor': history.push('/doctor-dashboard'); break; // Doctor Dashboard
                    case 'Recipient': history.push('/recipient-dashboard'); break; // Recipient/Triage
                    case 'Patient': history.push('/patient-dashboard'); break; // Patient Dashboard
                    default: history.push('/admin-dashboard');
                }
            }
        } catch (error: any) {
            console.error("Auth Error:", error);
            setToastMessage(error.response?.data?.detail || "Authentication failed");
            setShowToast(true);
        } finally {
            setLoading(false);
        }
    };

    return (
        <IonPage className="auth-page">
            <IonContent className="ion-padding auth-content">
                <div className="auth-container">
                    <IonCard className="auth-card">
                        <IonCardHeader>
                            <IonCardTitle className="auth-title">
                                {mode === 'login' ? 'Welcome Back' : 'Create Account'}
                            </IonCardTitle>
                        </IonCardHeader>

                        <IonSegment value={mode} onIonChange={e => setMode(e.detail.value as any)} className="auth-segment">
                            <IonSegmentButton value="login">Login</IonSegmentButton>
                            <IonSegmentButton value="signup">Sign Up</IonSegmentButton>
                        </IonSegment>

                        <IonCardContent>
                            <div className="auth-form">
                                {mode === 'signup' && (
                                    <IonItem className="auth-item">
                                        <IonLabel position="floating">Full Name</IonLabel>
                                        <IonInput value={fullName} onIonChange={e => setFullName(e.detail.value!)} />
                                    </IonItem>
                                )}

                                <IonItem className="auth-item">
                                    <IonLabel position="floating">Email</IonLabel>
                                    <IonInput type="email" value={email} onIonChange={e => setEmail(e.detail.value!)} />
                                </IonItem>

                                <IonItem className="auth-item">
                                    <IonLabel position="floating">Password</IonLabel>
                                    <IonInput type="password" value={password} onIonChange={e => setPassword(e.detail.value!)} />
                                </IonItem>

                                {mode === 'signup' && (
                                    <IonItem className="auth-item">
                                        <IonLabel>I am a:</IonLabel>
                                        <IonSelect value={role} onIonChange={e => setRole(e.detail.value)}>
                                            <IonSelectOption value="Patient">Patient</IonSelectOption>
                                            <IonSelectOption value="Recipient">Triage Officer (Recipient)</IonSelectOption>
                                            <IonSelectOption value="Doctor">Doctor</IonSelectOption>
                                            <IonSelectOption value="Admin">Admin</IonSelectOption>
                                        </IonSelect>
                                    </IonItem>
                                )}

                                {mode === 'signup' && role === 'Patient' && (
                                    <>
                                        <IonItem className="auth-item">
                                            <IonLabel position="floating">Phone Number</IonLabel>
                                            <IonInput value={phoneNumber} onIonChange={e => setPhoneNumber(e.detail.value!)} />
                                        </IonItem>
                                        <IonItem className="auth-item">
                                            <IonLabel position="floating">Age</IonLabel>
                                            <IonInput type="number" value={age} onIonChange={e => setAge(e.detail.value!)} />
                                        </IonItem>
                                        <IonItem className="auth-item">
                                            <IonLabel>Gender</IonLabel>
                                            <IonSelect value={gender} onIonChange={e => setGender(e.detail.value)}>
                                                <IonSelectOption value="Male">Male</IonSelectOption>
                                                <IonSelectOption value="Female">Female</IonSelectOption>
                                                <IonSelectOption value="Other">Other</IonSelectOption>
                                            </IonSelect>
                                        </IonItem>
                                    </>
                                )}

                                {mode === 'signup' && role === 'Doctor' && (
                                    <>
                                        <IonItem className="auth-item">
                                            <IonLabel>Department</IonLabel>
                                            <IonSelect value={departmentId} onIonChange={e => setDepartmentId(e.detail.value)}>
                                                {departments.map((dept) => (
                                                    <IonSelectOption key={dept.department_id} value={dept.department_id}>
                                                        {dept.name}
                                                    </IonSelectOption>
                                                ))}
                                            </IonSelect>
                                        </IonItem>
                                        <IonItem className="auth-item">
                                            <IonLabel position="floating">Specialization</IonLabel>
                                            <IonInput value={specialization} onIonChange={e => setSpecialization(e.detail.value!)} />
                                        </IonItem>
                                        <IonItem className="auth-item">
                                            <IonLabel position="floating">Experience (years)</IonLabel>
                                            <IonInput type="number" value={experienceYears} onIonChange={e => setExperienceYears(e.detail.value!)} />
                                        </IonItem>
                                    </>
                                )}

                                <div className="ion-padding-top">
                                    <IonButton expand="block" onClick={handleAuth} className="auth-btn">
                                        {mode === 'login' ? 'Sign In' : 'Register'}
                                    </IonButton>
                                </div>
                            </div>
                        </IonCardContent>
                    </IonCard>
                </div>

                <IonLoading isOpen={loading} message={'Please wait...'} />
                <IonToast
                    isOpen={showToast}
                    onDidDismiss={() => setShowToast(false)}
                    message={toastMessage}
                    duration={2000}
                    color="danger"
                />
            </IonContent>
        </IonPage>
    );
};

export default Auth;
