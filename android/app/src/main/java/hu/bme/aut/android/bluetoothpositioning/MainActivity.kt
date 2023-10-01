package hu.bme.aut.android.bluetoothpositioning

import android.content.ContentValues.TAG
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.net.DatagramPacket
import java.net.DatagramSocket

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp {
                ReceivedPacketView()
            }
        }
    }
}

@Composable
fun MyApp(content: @Composable () -> Unit) {
    MaterialTheme {
        Surface {
            content()
        }
    }
}

@Composable
fun ReceivedPacketView() {
    var packetData by remember { mutableStateOf("Awaiting packet...") }

    val context = LocalContext.current
    LaunchedEffect(key1 = context) {
        CoroutineScope(Dispatchers.IO).launch {
            val socket = DatagramSocket(9902)
            val buffer = ByteArray(1024)
            val packet = DatagramPacket(buffer, buffer.size)

            while (true) {
                socket.receive(packet)
                val message = String(packet.data, 0, packet.length)
                packetData = message
                Log.d(TAG, packetData)
            }

            // Don't forget to close the socket
            socket.close()
        }
    }

    Text(text = packetData)
}
