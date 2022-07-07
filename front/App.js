import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import BottomTabHome from './navigation/home/BottomTabHome';
import JoinView from './pages/JoinView';
import LoginView from './pages/LoginView';

export default function App() {
  // const [isLoading, setLoading] = useState(false);
  // useEffect(() => {
  //   setTimeout(() => {setLoading(true)}, 2000);
  // })
  const Stack = createStackNavigator();
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="BottomTabHome" screenOptions={{ headerShown: false }}>
        {/* initialRouteName: 이 Stack의 초기 view설정 */}
        <Stack.Screen name="LoginView" component={LoginView} />
        <Stack.Screen name="JoinView" component={JoinView} />
        <Stack.Screen name="BottomTabHome" component={BottomTabHome} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
