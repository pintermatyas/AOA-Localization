package hu.bme.aut.android.bluetoothpositioning

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Log
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import java.io.File
import java.io.FileInputStream
import java.io.IOException

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImageSelectionScreen(
    onConfirm: (Bitmap, Coordinate, Coordinate) -> Unit
) {
    val context = LocalContext.current
    val imageBitmap = remember { mutableStateOf<Bitmap?>(null) }
    var topRightX by remember { mutableStateOf("") }
    var topRightY by remember { mutableStateOf("") }
    var bottomLeftX by remember { mutableStateOf("") }
    var bottomLeftY by remember { mutableStateOf("") }
    imageBitmap.value = loadImageFromInternalStorage(context)
    val screenWidth = LocalConfiguration.current.screenWidthDp
    val screenHeight = LocalConfiguration.current.screenHeightDp

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent(),
        onResult = { uri: Uri? ->
            saveImageToInternalStorage(context, uri!!)
            imageBitmap.value = loadImageFromInternalStorage(context)
        }
    )

    Box(
        modifier = Modifier.fillMaxSize()
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Button(
                onClick = {
                    launcher.launch("image/*")
                }
            ) {
                Text(text = "Select Image")
            }

            imageBitmap.value?.let { bitmap ->

                Image(
                    modifier = Modifier.size((screenHeight/3).dp),
                    bitmap = bitmap.asImageBitmap(),
                    contentDescription = "some useful description",
                    contentScale = ContentScale.Fit,
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            Row (
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                TextField(
                    value = topRightX,
                    onValueChange = { topRightX = it },
                    label = { Text("Top Right X") },
                    modifier = Modifier.width((screenWidth/2).dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)

                )
                TextField(
                    value = topRightY,
                    onValueChange = { topRightY = it },
                    label = { Text("Top Right Y") },
                    modifier = Modifier.width((screenWidth/2).dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row (
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                TextField(
                    value = bottomLeftX,
                    onValueChange = { bottomLeftX = it },
                    label = { Text("Bottom Left X") },
                    modifier = Modifier.width((screenWidth/2).dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )
                TextField(
                    value = bottomLeftY,
                    onValueChange = { bottomLeftY = it },
                    label = { Text("Bottom Left Y") },
                    modifier = Modifier.width((screenWidth/2).dp),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )

            }
            Button(
                onClick = {

                    try {
                        val topRightXValue = topRightX.toFloat()
                        val topRightYValue = topRightY.toFloat()
                        val bottomLeftXValue = bottomLeftX.toFloat()
                        val bottomLeftYValue = bottomLeftY.toFloat()
                        onConfirm(
                            imageBitmap.value!!,
                            Coordinate(topRightXValue, topRightYValue),
                            Coordinate(bottomLeftXValue, bottomLeftYValue)
                        )
                        val message = "Valid coordinate input!"
                        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
                    } catch (e: NumberFormatException) {
                        val message = "Invalid coordinate input! Make sure all input coordinates are valid numbers!"
                        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
                        Log.e("ImageSelectionScreen", message)
                    }

                }
            ) {
                Text(text = "Confirm input")
            }

        }
    }

}

fun saveImageToInternalStorage(context: Context, uri: Uri) {
    val inputStream = context.contentResolver.openInputStream(uri)
    val outputStream = context.openFileOutput("image.jpg", Context.MODE_PRIVATE)
    inputStream?.use { input ->
        outputStream.use { output ->
            input.copyTo(output)
        }
    }
}

fun loadImageFromInternalStorage(context: Context): Bitmap? {
    try {
        val file = File(context.filesDir, "image.jpg")
        if (file.exists()) {
            val inputStream = FileInputStream(file)
            return BitmapFactory.decodeStream(inputStream)
        }
    } catch (e: IOException) {
        e.printStackTrace()
    }
    return null
}
