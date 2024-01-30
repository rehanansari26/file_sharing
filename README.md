## 📁 File Sharing

### 🏷️ Use Case Title: 
**Managing and Accessing Technical Drawings through File Sharing System**

### 🎭 Actors:
- **Supplier**
- **Purchase Department/Concerned Person** (acting as System Administrator)

### 🎯 Objective:
To enable the Purchase Department or a concerned person to effectively share technical drawings with suppliers, and for suppliers to access and view these drawings in the File Sharing System via the Supplier Portal.

### 🛑 Preconditions:
- Suppliers are registered with login credentials for the Supplier Portal.
- The Purchase Department or the designated concerned person has system administrator access to upload and share drawings.

### 🔄 Main Flow:

#### Admin-Related Tasks:
1. **Admin Prepares and Shares Drawing:**
    - 🚪 The admin logs into the system and navigates to 'Drawing Sharing DocType'.
    - 🔍 They select the intended item. If a drawing is already attached to this item, it is automatically fetched; if not, the system displays 'file not found'.
    - 🖇️ The admin then links the drawing to the item, choosing to share it based on a specific date or view-based access.

2. **System Notifies Supplier:**
    - 📨 Once the drawing is linked and shared, the system sends a notification to the supplier.

#### Supplier-Related Tasks:
1. **Supplier Portal:**
    - 🌐 The supplier logs into their portal.
    - 🔎 The supplier locates and views the drawing.
    - 📥 The supplier can interact with the drawing, including downloading, depending on permissions.
    
### ✅ Postconditions:
- The drawing is successfully uploaded and shared by the Purchase Department or concerned person, and accessed by the supplier.
- The system logs the activity related to the drawing for audit and tracking purposes.
  

![diagram](https://github.com/rehanansari26/File-Sharing/assets/110723484/f5af1ed9-4061-42ed-a7c4-32a11e2d62e0)



## 🌟 Features

- **📄 File Support:**
  - 📑 Documents: Supports PDF files for document sharing.
  - 🌐 3D Models: Utilizes the model viewer library to display .glb files, enhancing the visualization of 3D models.
 
- **🔗 Dependencies:**
   - [🔩 Frappe Framework](https://github.com/frappe/frappe)
   - [📊 ERPNext App](https://github.com/frappe/erpnext)

#### License

mit
