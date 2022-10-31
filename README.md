<h1 align="center">🗨️ Say Something Submod</h1>
<h3 align="center">Ask your Monika to say something and pose for you~</h3>

<p align="center">
  <a href="https://github.com/friends-of-monika/mas-saysomething/releases/latest">
    <img alt="Latest release" src="https://img.shields.io/github/v/release/friends-of-monika/mas-saysomething">
  </a>
  <a href="https://github.com/friends-of-monika/mas-saysomething/releases">
    <img alt="Release downloads" src="https://img.shields.io/github/downloads/friends-of-monika/mas-saysomething/total">
  </a>
  <a href="https://www.reddit.com/r/MASFandom/comments/yeqld8/heya_people_say_something_submod_is_out">
    <img alt="Reddit badge" src="https://img.shields.io/badge/dynamic/json?label=%F0%9D%97%8B%2Fmasfandom%20post&query=%24[0].data.children[0].data.score&suffix=%20upvotes&url=https%3A%2F%2Fwww.reddit.com%2Fr%2FMASFandom%2Fcomments%2Fyeqld8%2Fheya_people_say_something_submod_is_out.json&logo=reddit&style=social">
  </a>
  <a href="https://github.com/friends-of-monika/mas-saysomething/blob/main/LICENSE.txt">
    <img alt="MIT license badge" src="https://img.shields.io/badge/License-MIT-lightgrey.svg">
  </a>
  <a href="https://dcache.me/discord">
    <img alt="Discord server" src="https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=shield">
  </a>
  <a href="https://ko-fi.com/Y8Y15BC52">
    <img alt="Ko-fi badge" src="https://ko-fi.com/img/githubbutton_sm.svg" height="20">
  </a>
</p>


## 🌟 Features

* Ask your Monika to say anything for you~
* Comes with built-in expression changer!
* Position switch that lets you place your Monika's table wherever you want it.
* Supports multiple lines input~
* [Allows viewing expression code][15] to aid submod development.

## 🖼️ Screenshots

![Monika is wondering, what is that menu...][12]
![Monika is impressed][13]

## ❓ Installing

1. Go to [the latest release page][6] and scroll to Assets section.
2. Download `say-something-VERSION-MASVERSION.zip` file for your current MAS
   version.
3. Drag and drop `game/` folder from it into your DDLC folder.

   **NOTE:** make sure you don't drag it *into `game`*!
4. You're all set!~

## 🔧 Enabling expression codes

To enable expression code display, your MAS has to be *in developer mode*. To
enable this mode, create file `dev_devmode.rpy` in `game/Submods` with the
following content:

```renpy
init python:
    config.developer = True
```

Save and close this file. Restart the game, and now you'll have 'Show expression
code' option displayed in Submods settings section, tick it and you'll have
expression codes shown!~

*Why so complex?* This is done to minimize immersion breaking expression
selector screen already makes and hide this from users who are not submod
developers and who do not need some obscure text displaying on their selector
screen.

## 🏅 Special thanks

Say Something Submod authors, maintainers and contributors express their
gratitude to the following people:
* [SteveeWasTaken][1] &mdash; [MAS Custom Text][2] submod and original idea.
* [MaximusDecimus][3] &mdash; [MAS Custom Text Revamp][4] submod.

Additionally, we thank these people for testing the submod before its public
release:
* [Otter][5] &mdash; early access preview.
* [DJMayJay][14] &mdash; early access preview.
* TheGuy &mdash; early access preview.

## 💬 Join our Discord

We're up to chat! Come join submod author's Discord server [here][8] or come to chat at Friends
of Monika Discord server [here][9].

[![Discord server invitation][10]][8]
[![Discord server invitation][11]][9]

[1]: https://github.com/SteveeWasTaken
[2]: https://github.com/SteveeWasTaken/mas-custom-text
[3]: https://github.com/AzhamProdLive
[4]: https://github.com/AzhamProdLive/AzhamMakesTrash-Submods/tree/main/Custom%20Text%20Revamp
[5]: https://github.com/my-otter-self
[6]: https://github.com/friends-of-monika/mas-saysomething/releases/latest
[7]: https://github.com/PencilMario
[8]: https://dcache.me/discord
[9]: https://mon.icu/discord
[10]: https://discordapp.com/api/guilds/1029849988953546802/widget.png?style=banner3
[11]: https://discordapp.com/api/guilds/970747033071804426/widget.png?style=banner3
[12]: doc/screenshots/1.png
[13]: doc/screenshots/2.png
[14]: https://github.com/mayday-mayjay
[15]: https://github.com/friends-of-monika/mas-saysomething#-enabling-expression-codes