package org.christmanai.awarenistic

import android.Manifest
import android.app.Activity
import android.content.ComponentName
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/**
 * Awarenistic. Aware for you.
 * Let her watch the apps you choose, hand her anything you are unsure about, and read her card.
 */
class MainActivity : Activity() {
    private lateinit var access: TextView
    private lateinit var card: TextView
    private lateinit var message: EditText
    private lateinit var sender: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val pad = (16 * resources.displayMetrics.density).toInt()
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }

        column.addView(text("Awarenistic", 26f))
        column.addView(text("Aware for you. She reads the messages strangers send you and speaks up when one reads like a scam. Nothing she reads leaves this phone.", 16f))

        access = text("", 15f)
        column.addView(access)
        column.addView(button("Let her watch your messages") {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        })
        if (Build.VERSION.SDK_INT >= 33) {
            column.addView(button("Let her speak up") {
                requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1)
            })
        }

        column.addView(text("Apps she watches", 18f))
        val chosen = Her.watched(this).toMutableSet()
        for ((pkg, label) in Her.WATCHABLE) {
            column.addView(CheckBox(this).apply {
                text = label
                isChecked = pkg in chosen
                setOnCheckedChangeListener { _, on ->
                    if (on) chosen += pkg else chosen -= pkg
                    Her.setWatched(this@MainActivity, chosen)
                }
            })
        }

        column.addView(text("Hand her a message", 18f))
        sender = EditText(this).apply { hint = "Who sent it" }
        message = EditText(this).apply { hint = "Paste the message"; minLines = 3 }
        column.addView(sender)
        column.addView(message)
        column.addView(button("Read it") { readNow() })

        card = text("", 16f)
        column.addView(card)

        setContentView(ScrollView(this).apply { addView(column) })
        take(intent)
    }

    override fun onResume() {
        super.onResume()
        access.text = if (canWatch()) "She is watching the apps you chose." else "She is not watching yet. Give her notification access."
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        take(intent)
    }

    /** A card she raised, or a message shared to her from another app. */
    private fun take(intent: Intent?) {
        intent ?: return
        intent.getStringExtra(Her.EXTRA_CARD)?.let { card.text = it; return }
        if (intent.action == Intent.ACTION_SEND) {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { message.setText(it); readNow() }
        }
    }

    private fun readNow() {
        val text = message.text.toString().trim()
        if (text.isEmpty()) { card.text = "Paste the message first."; return }
        val who = sender.text.toString().trim().ifEmpty { "someone" }
        card.text = "Reading…"
        Thread {
            val shown = try {
                Her.read(this, text, who).cardText
            } catch (e: Exception) {
                "She could not read it: ${e.message}"
            }
            runOnUiThread { card.text = shown }
        }.start()
    }

    private fun canWatch(): Boolean {
        val enabled = Settings.Secure.getString(contentResolver, "enabled_notification_listeners").orEmpty()
        return enabled.contains(ComponentName(this, WatchService::class.java).flattenToString())
    }

    private fun text(s: String, size: Float) = TextView(this).apply {
        text = s
        textSize = size
        setPadding(0, 12, 0, 12)
        layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT)
    }

    private fun button(label: String, onClick: () -> Unit) = Button(this).apply {
        text = label
        setOnClickListener { onClick() }
    }
}
