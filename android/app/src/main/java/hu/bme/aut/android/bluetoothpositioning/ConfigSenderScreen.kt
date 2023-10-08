package hu.bme.aut.android.bluetoothpositioning

import android.annotation.SuppressLint
import androidx.compose.runtime.*
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.window.DialogProperties

@SuppressLint("UnusedMaterial3ScaffoldPaddingParameter")
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConfigureFieldsScreen() {
    val context = LocalContext.current
    var showDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = "Configure New Anchor") },
                actions = {
                    IconButton(onClick = { showDialog = true }) {
                        Icon(Icons.Filled.Done, contentDescription = "Save")
                    }
                }
            )
        },
        content = {
            Box(
                modifier = Modifier.fillMaxSize()
                    .padding(top = 72.dp)
            ){
                ConfigureFieldsForm()
            }
        }
    )

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text(text = "Confirmation") },
            text = { Text(text = "New Anchor has been configured!") },
            confirmButton = {
                Button(onClick = { showDialog = false }) {
                    Text("OK")
                }
            },
            properties = DialogProperties(
                dismissOnBackPress = true,
                dismissOnClickOutside = true
            )
        )
    }
}


@Composable
fun ConfigureFieldsForm() {
    var anchorId by remember { mutableStateOf("") }
    var x by remember { mutableStateOf("") }
    var y by remember { mutableStateOf("") }
    var z by remember { mutableStateOf("") }
    var angleAzimuth by remember { mutableStateOf("") }
    var angleElevation by remember { mutableStateOf("") }
    var angleRotation by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        TextFieldWithLabel("Anchor ID", anchorId) { anchorId = it }
        TextFieldWithLabel("X", x) { x = it }
        TextFieldWithLabel("Y", y) { y = it }
        TextFieldWithLabel("Z", z) { z = it }
        TextFieldWithLabel("Angle Azimuth", angleAzimuth) { angleAzimuth = it }
        TextFieldWithLabel("Angle Elevation", angleElevation) { angleElevation = it }
        TextFieldWithLabel("Angle Rotation", angleRotation) {
            angleRotation = it
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TextFieldWithLabel(label: String, value: String, onValueChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text(label) }
    )
}

@Preview
@Composable
fun PreviewConfigureFieldsScreen() {
    ConfigureFieldsScreen()
}
