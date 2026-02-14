import { IonApp, IonRouterOutlet } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { Route } from 'react-router-dom';
import PatientIntake from './pages/PatientIntake';
import Dashboard from './pages/Dashboard';
import Doctors from './pages/Doctors';
import LandingPage from './pages/LandingPage';

const App: React.FC = () => (
  <IonApp>
    <IonReactRouter>
      <IonRouterOutlet>
        <Route path="/intake" component={PatientIntake} exact />
        <Route path="/dashboard" component={Dashboard} exact />
        <Route path="/doctors" component={Doctors} exact />
        <Route path="/" component={LandingPage} exact />
      </IonRouterOutlet>
    </IonReactRouter>
  </IonApp>
);

export default App;
