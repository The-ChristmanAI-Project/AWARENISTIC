package org.christmanai.awarenistic

import android.Manifest
import android.app.Activity
import android.content.ActivityNotFoundException
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
    private lateinit var trusted: EditText
    private lateinit var share: Button
    private lateinit var shareNote: TextView
    private var route: Her.Route? = null

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

        column.addView(text("Someone you trust", 18f))
        trusted = EditText(this).apply {
            hint = "Their phone number or email"
            setText(Her.trusted(this@MainActivity))
        }
        column.addView(trusted)
        column.addView(button("Save") {
            Her.setTrusted(this, trusted.text.toString())
            shareNote.text = if (trusted.text.isBlank()) "No one named yet." else "Saved. Her cards can go to them."
        })

        column.addView(text("Hand her a message", 18f))
        sender = EditText(this).apply { hint = "Who sent it" }
        message = EditText(this).apply { hint = "Paste the message"; minLines = 3 }
        column.addView(sender)
        column.addView(message)
        column.addView(button("Read it") { readNow() })

        card = text("", 16f)
        column.addView(card)
        share = button("Show this to someone I trust") { sendToTrusted() }
        share.visibility = android.view.View.GONE
        column.addView(share)
        shareNote = text("", 14f)
        column.addView(shareNote)

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
        intent.getStringExtra(Her.EXTRA_CARD)?.let { shown ->
            card.text = shown
            val who = intent.getStringExtra(Her.EXTRA_WHO).orEmpty()
            if (who.isNotEmpty()) {
                Thread {
                    val r = try { Her.routeFor(this, who) } catch (e: Exception) { null }
                    runOnUiThread { showRoute(r) }
                }.start()
            }
            return
        }
        if (intent.action == Intent.ACTION_SEND) {
            intent.getStringExtra(Intent.EXTRA_TEXT)?.let { message.setText(it); readNow() }
        }
    }

    private fun readNow() {
        val text = message.text.toString().trim()
        if (text.isEmpty()) { card.text = "Paste the message first."; return }
        val who = sender.text.toString().trim().ifEmpty { "someone" }
        card.text = "Reading…"
        showRoute(null)
        Thread {
            var r: Her.Route? = null
            val shown = try {
                val reading = Her.read(this, text, who)
                r = reading.trusted
                reading.cardText
            } catch (e: Exception) {
                "She could not read it: ${e.message}"
            }
            runOnUiThread { card.text = shown; showRoute(r) }
        }.start()
    }

    /** The button shows only when her card can go to the person they trust; otherwise she says why. */
    private fun showRoute(r: Her.Route?) {
        route = r
        val ready = r?.ok == true
        share.visibility = if (ready) android.view.View.VISIBLE else android.view.View.GONE
        shareNote.text = when {
            r == null || ready -> ""
            else -> r.reason
        }
    }

    /** Opens their own texting or mail app with her card in it. They press send, not her. */
    private fun sendToTrusted() {
        val open = route?.let { Her.showSomeoneITrust(it) } ?: return
        try {
            startActivity(open)
        } catch (e: ActivityNotFoundException) {
            shareNote.text = "This phone has no app that can send that. Copy the card and show it to them."
        }
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
