package org.cedar.iconpack;

import android.app.Activity;
import android.os.Bundle;

/**
 * Openable entry point for the icon pack. Launchers discover the pack through
 * this activity's intent-filter actions (org.adw.launcher.themes etc.).
 */
public class ThemeActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
