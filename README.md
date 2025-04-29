# Blender View Align

## これは何？
Blenderの3Dビューで、ピック(選択)したオブジェクトに対して一発で視点を合わせたり、新しいTransform Orientationを作成したりできるアドオンだよ。

## インストール方法

1. 「Scripting」タブで新規テキストを作成して、このスクリプトを貼り付ける  
2. `Run Script` ボタンを押して実行する  
3. `N`パネルの「**Nylonheart**」タブに操作パネルが追加される

## 使い方

1. **Pick Object (Click)**: ピックしたいオブジェクトを選択して、このボタンを押すとターゲットとして登録  
2. **-Y / +Y / X / -X / Z / -Z**: 登録したオブジェクトのローカル座標軸をもとに、ワンクリックで視点を合わせる  
3. **Create / Switch Transform Orientation**:  
   - ピックしたオブジェクトを元に新しいTransform Orientation(カスタム座標系)を作成する  
   - 既に同名のTransform Orientationが存在する場合は、それに切り替える

## 🛠️ インストール手順 (NH_シリーズ共通)

この手順は、すべての **NH_ から始まるスクリプト** に共通です。

1. Blenderの「アドオンフォルダ」を開きます  
   - Windows:  
     `C:\Users\あなたのユーザー名\AppData\Roaming\Blender Foundation\Blender\<バージョン番号>\scripts\addons`
   - Mac:  
     `~/Library/Application Support/Blender/<バージョン番号>/scripts/addons`
   - Linux:  
     `~/.config/blender/<バージョン番号>/scripts/addons`

2. NH_から始まる `.py` ファイルをコピー

- 使用したい **NH_から始まる.pyファイル**（例：`NH_IDVertexColor.py`、`NH_CustomViewAlign.py`）を
- 上記の **addonsフォルダ** にそのままコピーします

  > 📂 フォルダごとではなく、**.pyファイル単体**を置きます！

3. Blenderを再起動します

4. アドオンを有効化する

1. Blenderのメニューから「**編集** → **プリファレンス** → **アドオン**」を開きます
2. 検索バーに `NH_` と入力してフィルターします
3. インストールしたアドオン（例：`NH_IDVertexColor` など）にチェックを入れて**有効化**します

✨ これで完了！

NH_シリーズのアドオンがすぐに使えるようになります。
