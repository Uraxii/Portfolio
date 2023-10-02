using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Subscriber : MonoBehaviour
{
    public void StateChange(string state)
    {
        Debug.Log(state);
    }

    // Start is called before the first frame update
    void Start(){}

}
