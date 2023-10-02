using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.Events;

[System.Serializable]
public class MusicEvent : UnityEvent<string>
{
}

public class Publisher : MonoBehaviour
{
    [SerializeField]
    private string[] states = null;
    [SerializeField]
    private MusicEvent OnStateChange = null;

// OnGUI is called for rendering and handling GUI events.
    private void OnGUI()
    {

            foreach(var x in states)
            {
                if (GUILayout.Button("Change state to " + x))
                {
                    // If button pressed...

                    // New way to say if(OnEvent!=null){...}
                    // Null events mean the function does not exist on the subscriber
                    OnStateChange?.Invoke(x);
                }
            }
        }
    }
