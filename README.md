# Blender View Align

- **日本語 (Japanese)**
- **English**

---

## 日本語 (Japanese)

### これは何？
Blenderの3Dビューで、ピック(選択)したオブジェクトに対して一発で視点を合わせたり、新しいTransform Orientationを作成したりできるアドオンだよ。

### インストール方法

1. 「Scripting」タブで新規テキストを作成して、このスクリプトを貼り付ける  
2. `Run Script` ボタンを押して実行する  
3. `N`パネルの「**Nylonheart**」タブに操作パネルが追加される

### 使い方

1. **Pick Object (Click)**: ピックしたいオブジェクトを選択して、このボタンを押すとターゲットとして登録  
2. **-Y / +Y / X / -X / Z / -Z**: 登録したオブジェクトのローカル座標軸をもとに、ワンクリックで視点を合わせる  
3. **Create / Switch Transform Orientation**:  
   - ピックしたオブジェクトを元に新しいTransform Orientation(カスタム座標系)を作成する  
   - 既に同名のTransform Orientationが存在する場合は、それに切り替える

## English

### What is this?
An add-on for Blender that lets you quickly align the 3D view to a picked (selected) object’s local axes and create/switch custom Transform Orientations with a single click.

### Installation

1. Go to the “Scripting” tab in Blender and create a new text block  
2. Paste this script in and press `Run Script`  
3. Open the `N` panel. You will see a new tab labeled **Nylonheart**, which contains the add-on’s UI

### Usage

1. **Pick Object (Click)**: Select an object in the scene, then click this button to register it as the target  
2. **-Y / +Y / X / -X / Z / -Z**: Instantly align the view to the chosen object’s local axes  
3. **Create / Switch Transform Orientation**:
   - Creates a new Transform Orientation (custom coordinate system) based on the picked object  
   - If one with the same name already exists, it switches to that orientation instead
