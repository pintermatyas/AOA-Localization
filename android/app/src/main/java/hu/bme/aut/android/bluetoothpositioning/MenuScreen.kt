package hu.bme.aut.android.bluetoothpositioning

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController

@Composable
fun MenuScreen(
    navHostController: NavHostController,
    onConfigButton: () -> Unit,
    onMapButton: () -> Unit,
){
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Button(
            modifier = Modifier
                .height(50.dp)
                .width(200.dp),
            onClick = onMapButton,
        ) {
            Text("Map")
        }
        Spacer(modifier = Modifier.height(20.dp))
        Button(
            modifier = Modifier
                .height(50.dp)
                .width(200.dp),
            onClick = onConfigButton,
        ) {
            Text("Load new configuration")
        }
    }
}