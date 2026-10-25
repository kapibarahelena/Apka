package pl.szymon.traininghub

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { HubHome() } }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HubHome() {
    var selected by remember { mutableStateOf("Dzisiaj") }
    val tabs = listOf("Dzisiaj", "Historia", "Plan", "Trendy", "Integracje")
    Scaffold(topBar = { TopAppBar(title = { Text("Szymon Training Hub") }) }) { padding ->
        Column(Modifier.padding(padding).fillMaxSize().padding(16.dp)) {
            ScrollableTabRow(selectedTabIndex = tabs.indexOf(selected), edgePadding = 0.dp) {
                tabs.forEach { tab -> Tab(selected == tab, onClick = { selected = tab }, text = { Text(tab) }) }
            }
            Spacer(Modifier.height(16.dp))
            LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                item {
                    ElevatedCard(Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp)) {
                            Text(selected, style = MaterialTheme.typography.titleLarge)
                            Spacer(Modifier.height(8.dp))
                            Text(when (selected) {
                                "Dzisiaj" -> "Dashboard backendu: gotowość, ostatni trening i zalecenie pojawią się po skonfigurowaniu źródeł."
                                "Historia" -> "Historia aktywności Strava i dostępnych danych Garmin."
                                "Plan" -> "Plan tygodnia, wykonanie i pominięcie sesji."
                                "Trendy" -> "Tempo, tętno, obciążenie i regeneracja na osi czasu."
                                else -> "Status połączeń, zakres historii, ostatni import i błędy synchronizacji."
                            })
                            Spacer(Modifier.height(12.dp))
                            Text("Wersja 0.1.0 · szkielet natywny", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                }
                item {
                    OutlinedCard(Modifier.fillMaxWidth()) {
                        Column(Modifier.padding(16.dp)) {
                            Text("Następny krok", style = MaterialTheme.typography.titleMedium)
                            Text("Skonfiguruj adres backendu i klucz API. Dane kont nie są osadzone w aplikacji.")
                        }
                    }
                }
            }
        }
    }
}
