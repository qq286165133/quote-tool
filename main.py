import flet as ft

# ============ 价格表 ============
SMALL = [
    {"name": "一区·广东", "cities": ["广东","广州","深圳","东莞","佛山","惠州","珠海","中山","江门","汕头","湛江","茂名","肇庆","潮州","揭阳","梅州","汕尾","河源","阳江","清远","韶关","云浮"], "first": 8.5, "renew": 1.5},
    {"name": "二三区", "cities": ["上海","浙江","杭州","宁波","温州","江苏","南京","苏州","无锡","安徽","合肥","福建","福州","厦门","广西","南宁","湖北","武汉","湖南","长沙","江西","南昌","贵州","贵阳","河南","郑州","山东","济南","青岛","山西","太原","陕西","西安","四川","成都","云南","昆明","重庆","北京","天津","河北","石家庄","海南","海口"], "first": 9.3, "renew": 2.3, "default": True},
    {"name": "四区", "cities": ["甘肃","兰州","吉林","长春","辽宁","沈阳","大连","内蒙古","呼和浩特","黑龙江","哈尔滨","青海","西宁","宁夏","银川"], "first": 9, "renew": 3.5},
    {"name": "新疆", "cities": ["新疆","乌鲁木齐"], "first": 12, "renew": 8},
    {"name": "西藏", "cities": ["西藏","拉萨"], "first": 18, "renew": 7},
]

LARGE = [
    {"name": "一区·广东", "cities": ["广东","广州","深圳","东莞","佛山","惠州","珠海","中山","江门","汕头","湛江","茂名"], "first": 13, "renew": 2},
    {"name": "二三区+四区", "cities": [], "first": 18, "renew": 9, "default": True},
    {"name": "新疆", "cities": ["新疆","乌鲁木齐"], "first": 22, "renew": 12},
    {"name": "西藏", "cities": ["西藏","拉萨"], "first": 27, "renew": 23},
]

def find_zone(dest, large=False):
    if not dest:
        return None
    table = LARGE if large else SMALL
    for z in table:
        if z.get("default"):
            continue
        for c in z["cities"]:
            if c in dest or dest in c:
                return z
    return next((z for z in table if z.get("default")), SMALL[1])

def calc(L, W, H, t, dest=""):
    """计算报价，返回各项数值"""
    # 六面面积 m²
    S_cm2 = 2 * (L*W + L*H + W*H)
    S_m2 = S_cm2 / 10000
    
    # 材料成本
    material = S_m2 * 1.2 * t * 25
    
    # 实际重量
    actual_weight = S_m2 * 1.2 * t
    
    # 包装抛重
    is_large = False
    cargo = (L+5) * (W+5) * (H+5) / 8000
    if cargo >= 20:
        is_large = True
        cargo = (L+10) * (W+10) * (H+10) / 12000
    
    # 西藏单独处理
    if "西藏" in dest:
        cargo = (L+5)*(W+5)*(H+5) / 12000
    
    # 最终计费重量
    bill_weight = max(cargo, actual_weight)
    
    # 是否大件
    is_large_bill = bill_weight >= 20 or is_large
    if is_large_bill:
        # 大件重新按12000算抛重
        cargo = (L+10)*(W+10)*(H+10) / 12000
        bill_weight = max(cargo, actual_weight)
    
    # 找区域
    zone = find_zone(dest, is_large_bill)
    if not zone:
        zone = LARGE[1] if is_large_bill else SMALL[1]
    
    # 运费
    if is_large_bill:
        freight = zone["first"] + max(0, bill_weight - 1) * zone["renew"]
    else:
        bw = bill_weight
        if bw < 1:
            freight = zone["first"]
        else:
            freight = zone["first"] + (bw - 1) * zone["renew"]
    
    # 小件不足1kg按1kg
    if not is_large_bill and bill_weight < 1:
        bill_weight = 1
    
    total = material + freight
    
    return {
        "S_cm2": S_cm2,
        "S_m2": S_m2,
        "material": round(material, 2),
        "actual_weight": round(actual_weight, 2),
        "cargo": round(cargo, 2),
        "bill_weight": round(bill_weight, 2),
        "is_large": is_large_bill,
        "zone_name": zone["name"],
        "freight": round(freight, 2),
        "total": round(total, 2),
    }


class QuoteApp:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "亚克力报价工具"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        page.window_width = 400
        page.window_height = 700
        
        # 主题色
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_600,
                primary_container=ft.Colors.BLUE_50,
            )
        )
        
        # 输入控件
        self.length = ft.TextField(
            label="长 (cm)", 
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.STRAIGHTEN,
            border=ft.InputBorder.OUTLINE,
            width=150,
        )
        self.width = ft.TextField(
            label="宽 (cm)", 
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.STRAIGHTEN,
            border=ft.InputBorder.OUTLINE,
            width=150,
        )
        self.height = ft.TextField(
            label="高 (cm)", 
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.STRAIGHTEN,
            border=ft.InputBorder.OUTLINE,
            width=150,
        )
        self.thickness = ft.Dropdown(
            label="厚度",
            value="3",
            options=[
                ft.dropdown.Option("2", "2mm"),
                ft.dropdown.Option("3", "3mm"),
                ft.dropdown.Option("4", "4mm"),
                ft.dropdown.Option("5", "5mm"),
            ],
            width=150,
        )
        self.dest = ft.TextField(
            label="目的地（可选）",
            hint_text="例如：广东、浙江、北京...",
            prefix_icon=ft.Icons.LOCATION_ON,
            border=ft.InputBorder.OUTLINE,
            width=320,
        )
        
        # 显示结果
        self.area_text = ft.Text("", size=14)
        self.material_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.freight_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.total_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD)
        
        self.result_card = ft.Container(
            content=ft.Column([
                self.area_text,
                ft.Divider(height=1),
                self.material_text,
                ft.Divider(height=1),
                self.freight_text,
                ft.Divider(height=1, thickness=2),
                self.total_text,
            ], spacing=8),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
            padding=20,
            visible=False,
            width=340,
        )
        
        # 搭建页面
        page.add(
            ft.Row([ft.Icon(ft.Icons.HANDYMAN, color=ft.Colors.BLUE_600, size=32),
                   ft.Text("亚克力报价计算器", size=24, weight=ft.FontWeight.BOLD)], spacing=10),
            ft.Divider(height=2),
            ft.Text("尺寸", size=16, weight=ft.FontWeight.W_600),
            ft.ResponsiveRow([
                ft.Column([self.length], col={"sm": 4}),
                ft.Column([ft.Text("×", size=20, text_align=ft.TextAlign.CENTER)], col={"sm": 1}),
                ft.Column([self.width], col={"sm": 4}),
            ]),
            ft.Row([
                ft.Text("×", size=20),
                self.height,
            ], spacing=10),
            ft.Row([
                self.thickness,
                ft.Text(" 厚度", size=14),
            ]),
            ft.Divider(height=1),
            self.dest,
            ft.ElevatedButton(
                "开始算价",
                icon=ft.Icons.CALCULATE,
                on_click=self.calculate,
                style=ft.ButtonStyle(
                    padding=ft.Padding(30, 15, 30, 15),
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                width=340,
            ),
            self.result_card,
        )
    
    def calculate(self, e):
        try:
            L = float(self.length.value)
            W = float(self.width.value)
            H = float(self.height.value)
            t = int(self.thickness.value)
        except (ValueError, TypeError):
            self.show_error("请输入正确的尺寸数字")
            return
        
        dest = self.dest.value or ""
        result = calc(L, W, H, t, dest)
        
        self.area_text.value = f"📐 六面面积：{result['S_cm2']:.0f} cm² = {result['S_m2']:.4f} m²"
        self.material_text.value = f"🧱 材料成本：¥{result['material']:.2f}"
        
        if dest:
            self.freight_text.value = f"🚚 运费（{result['zone_name']}·{'大件' if result['is_large'] else '小件'}）：¥{result['freight']:.2f}"
            self.freight_text.value += f"\n   📦 实重{result['actual_weight']:.2f}kg | 抛重{result['cargo']:.2f}kg | 计费{result['bill_weight']:.2f}kg"
        else:
            self.freight_text.value = "🚚 运费：未输入目的地，暂不计算"
        
        self.total_text.value = f"💰 合计：¥{result['total']:.2f}"
        self.total_text.color = ft.Colors.RED_700
        
        self.result_card.visible = True
        self.page.update()
    
    def show_error(self, msg):
        self.result_card.visible = False
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg),
            bgcolor=ft.Colors.RED_700,
        )
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    QuoteApp(page)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=8500, host="0.0.0.0")
