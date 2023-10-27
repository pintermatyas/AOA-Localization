package hu.bme.aut.android.bluetoothpositioning

import android.content.ContentValues.TAG
import android.os.Bundle
import android.util.Log
import android.widget.Toast
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
import java.net.BindException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MyApp {
                ReceivedPacketView()
            }
        }
        sendUdpMessage("Subscribe", 9903)
    }

    override fun onResume() {
        super.onResume()
        sendUdpMessage("Subscribe", 9903)
    }
    override fun onPause() {
        super.onPause()
        sendUdpMessage("Unsubscribe", 9903)
    }

    override fun onStop() {
        super.onStop()
        // Send "Unsubscribe" when closing the app
        sendUdpMessage("Unsubscribe", 9903)
    }

    override fun onRestart() {
        super.onRestart()
        // Resubscribe if the application is opened again from the background
        sendUdpMessage("Subscribe", 9903)
    }

    private fun sendUdpMessage(message: String, port: Int) {
        Thread {
            try {
                val udpSocket = DatagramSocket()
                val serverAddr: InetAddress = InetAddress.getByName("10.42.0.1")
                val buf: ByteArray = message.toByteArray()
                val packet = DatagramPacket(buf, buf.size, serverAddr, port)
                udpSocket.send(packet)
                udpSocket.close()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
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
            try{
                val socket = DatagramSocket(9902)
                val buffer = ByteArray(1024)
                val packet = DatagramPacket(buffer, buffer.size)

                while (true) {
                    socket.receive(packet)
                    val message = String(packet.data, 0, packet.length)
                    if(!message.contains("nan")){
                        packetData = message
                        Log.d(TAG, packetData)
                    } else {
                        Log.e(TAG, message)
                    }
                }

                socket.close()
            }
            catch (e: BindException){
                e.printStackTrace()
            }
        }
    }


    if (packetData.contains("Awaiting")){
        Text(text=packetData)
    }
    else{
        MapScreen(data = packetData)
    }
}
