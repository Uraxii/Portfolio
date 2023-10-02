using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class ModifyTextColor: MonoBehaviour
{

    public Text text;
    public Color activeColor;
    public Color hoverColor;
    private Color inactiveColor;
    private Color currentColor;

    private bool active;


    public void OnClick()
    {
        if (!active)
        {
            text.color = activeColor;
            currentColor = activeColor;
        }
        else
        {
            text.color = inactiveColor;
            currentColor = inactiveColor;
        }
        active = !active;
    }

    public void OnEnter()
    {
        text.color = hoverColor;
    }

    public void OnExit()
    {
        text.color = currentColor;
    }

    private void Start() {
        active = false;
        inactiveColor = text.color;
        currentColor = text.color;
    }
}
