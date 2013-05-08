Why is ambilight using a group slow?
------------------------------------

Short answer: the bridge can't keep up

Long answer: In ambilight mode the add-on continually tries to adjust the color of the lights. It might do so approx 3 times per second. Everytime it will tell the bridge to update the color, and the bridge will do so as fast as possible.

If the bridge tries to update the color of a complete group, every once in a while it'll take the bridge 1.5 second to complete the update (in a quick test I did this happens 1 out of 5 times, or the bridge responded quickly but with an error). The add-on will continue to request an update 3 times/second, and the bridge gets out of sync with the video.

I would like to use 1 lamp for ambilight, and turn 2 other lights off
---------------------------------------------------------------------

Say you have 8 bulbs, 3 of them are in the living room and 1 of those is next to the television. When playback starts 2 lights in the living room should be dimmed, and the one next to the television should be used as an ambilight.

 - Create a custom group with the two lights you wish to turn off (see below)
 - Configure ambilight mode for the single bulb next to the television
 - In the advanced section, enable "Dim a group of lights when playback starts"
 - Set the "Group ID to dim" to the ID of the newly created group in step 1

Creating a custom group
-----------------------

The add-on supports using "custom groups". By default the Hue only has one group, called group "0". This means "all lights". This is the group the add-on uses when the option "use all lights" is selected. But if you want more flexibility you might want to create your own group. Eg you have 8 bulbs in total, but only the 4 in the living room should be controlled by this add-on.

Creating custom groups is not (yet) officially support. It is therefore not possible to do from the official Hue application. You can do it yourself but you'll need to some manual steps.

First, identify your bridge IP and bridge User. You can find both in the settings panel of the add-on.

In the following example I used:
 - bridge IP: 192.168.10.10
 - bridge User: 62cbb1fb7191475ea13181e18848cd7

If you open up a browser, visit the following URL to confirm the IP and user are correct:

`http://*bridge_ip*/api/*bridge_user*/`

So in the example:

`http://192.168.10.10/api/762cbb1fb7191475ea13181e18848cd7`

You should see a page with all the configuration settings of the Hue bridge. Somewhere it should say "groups":{}. Meaning you have no custom groups.

To add a group open up a Terminal. Say you want to add a new group called "Living room" containing lights 1 and 2. To do so, run the following command:

`curl --request POST "http://192.168.10.10/api/762cbb1fb7191475ea13181e18848cd7/groups" --data '{"name":"Living Room","lights":["1", "2"]}' -H "Content-Type: application/json"`

The bridge should return:

`[{"success":{"id":"/groups/1"}}]`

You can confirm the group is created by visiting the website:

`http://192.168.10.10/api/762cbb1fb7191475ea13181e18848cd7/groups/1`

Now, **you'll have to restart the bridge before the group actually works**

Check if the group is working by issuing the following request

`curl --request PUT "http://192.168.10.10/api/762cbb1fb7191475ea13181e18848cd7/groups/1/action" --data '{"on":true,"bri":255,"hue":65000}' -H "Content-Type: application/json"`

That should turn the bulbs in this group bright red.
