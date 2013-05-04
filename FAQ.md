Creating a custom group
-----------------------

The add-on supportrs using "custom groups". By default the Hue only has one group, called group "0". This means "all lights". This is the group the add-on uses when the option "use all lights" is selected. But if you want more flexibility you might want to create your own group. Eg you have 8 bulbs in total, but only the 4 in the living room should be controlled by this add-on.

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

I would like to use only 2 lamps for ambilight, and turn 2 other lights off
---------------------------------------------------------------------------

Say you have 8 bulbs, 4 of them are in the living room and 2 of those are next to the television. When playback starts 2 lights in the living room should be dimmed, and the two next to the television should be used as ambilights.

You'll have to create two custom groups:
 - a group with the 2 lights you want dimmed
 - a group with the 2 lights you want to use for ambilight

(See above on how to create a custom group, in the example the lights to be dimmed is group 2, and the 2 lights next to the television is group 1)

Configure the add-on in ambilight mode and set it to "use all lights". Now go to the advanced section and override the group ID of "use all lights" to group 1 (the 2 lights next to the television). Ambilight is now enabled to only use those two lights.

In the advanced section toggle the option "Ambilight: dim all lights when playback starts" and set "Ambilight: group ID when dimming lights" to group 2.

**Using ambilight for a group is slow**, it works way better if you use it with a single bulb. (It appears the bridge is slow when updating the configuration of a group)
