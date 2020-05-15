import math
import matplotlib.pyplot as plt
import numpy as np

def error_estimation_func(W, V, p):  # Оценка погрешности (В методичке S)
    return (W - V) / (2 ** (p) - 1)


def double_calc(f, x, y, h, param_a):  # Двойной подсчет методом РК*
    k1, k2, k3, k4 = calc_coeff(f, x, y, h / 2, param_a)
    tmp_x = x + h / 2
    tmp_y = y + (k1 + k2 + k2 + k3 + k3 + k4) / 6
    k1, k2, k3, k4 = calc_coeff(f, tmp_x, tmp_y, h / 2, param_a)
    tmp_x = tmp_x + h / 2
    tmp_y = tmp_y + (k1 + k2 + k2 + k3 + k3 + k4) / 6
    return tmp_y


def split_step(S, p, eps):  # p - порядок метода
    tmp = eps / (2 ** (p + 1))
    if abs(S) > eps:
        return 3
    if tmp <= abs(S) and abs(S) <= eps:
        return 1
    if abs(S) < tmp:
        return 2


def calc_coeff(f, x, y, h, param_a):  # Подсчет коэффициентов РК*
    k1 = h * f(x, y, param_a)
    k2 = h * f(x + 0.5 * h, y + 0.5 * k1, param_a)
    k3 = h * f(x + 0.5 * h, y + 0.5 * k2, param_a)
    k4 = h * f(x + h, y + k3, param_a)
    return k1, k2, k3, k4

def rk4_v2(f, x0, y0, x1, h, max_n, eps_bord, flag_inc_step, flag_deg_step, eps, param_a):
    info = dict.fromkeys(
        ['n', 'inc', 'deg', 'max err est', 'X on max err est', 'min err est', 'X on min err est', 'x1', 'eps',
         'eps_bord', 'a', 'b'])  # err est - оценка погрешности
    table = dict.fromkeys(
        ['X', 'Y', 'H', 'W', 'W-V', 'S', 'inc_count', 'deg_count', 'local'])  # См. Методичу страница 13
    info['n'] = 0
    info['inc'] = 0
    info['deg'] = 0
    info['max err est'] = np.float64(0)
    info['min err est'] = np.float64(999)
    info['x1'] = x1
    info['eps'] = eps
    info['eps_bord'] = eps_bord
    #info['a'] = param_a
    #info['b'] = param_b
    # Выделение памяти

    table['W-V'] = [0] * (max_n + 1)
    vx = [0] * (max_n + 1)  # Значение x для каждого шага
    vy = [0] * (max_n + 1)  # Значение y для каждого шага
    vh = [0] * (max_n + 1)  # Значение h для каждого шага
    vw = [0] * (max_n + 1)  # Значение w для каждого шага
    v_ic = [0] * (max_n + 1)  # Значение inc_count для каждого шага
    v_dc = [0] * (max_n + 1)  # Значение deg_count для каждого шага
    vs = [0] * (max_n + 1)  # Значение s для каждого шага
    vx[0] = x = x0
    vy[0] = y = y0
    i = 1
    vh[0] = h
    ccc = 0
    while (i) < max_n:
        v_ic[i] = info['inc']
        v_dc[i] = info['deg']
        # Проверка выхода за границу
        if x + h > x1:
            h = h / 2
            v_dc[i] = info['deg'] = info['deg'] + 1
            continue
        k1, k2, k3, k4 = calc_coeff(f, x, y, h, param_a)  # Подсчет коэффициентов для метода РК*
        #k1, k2, k3, k4 = calc_coeff(f, x, y, h, param_a, param_b)
        w = double_calc(f, x, y, h, param_a)
        #w = double_calc(f, x, y, h, param_a, param_b)
        vx[i] = x = x + h
        vs[i] = err_est = error_estimation_func(w, y + (k1 + k2 + k2 + k3 + k3 + k4) / 6, 4)

        # Выбор максимальной и минимальной оценки погрешности

        if abs(info['max err est']) < abs(err_est):
            info['max err est'] = abs(err_est)
            info['X on max err est'] = x
        if abs(info['min err est']) > abs(err_est):
            info['min err est'] = abs(err_est)  # Добавить условие чтобы сюда не ставил ошибку из начальной точки
            info['X on min err est'] = x  # Подсчет следующей точки с двойной точностью

        # Изменение шага
        if flag_deg_step != 0:
            if (split_step(err_est, 4, eps) == 3):  # Третий случай
                x = x - h
                h /= 2
                # v_dc[i] = info['deg'] = info['deg']+1
                info['deg'] = info['deg'] + 1
                continue  # Прераваем текущую итерацию цикла т.е. не увидичиваем i уменьшаем шаг
        if flag_inc_step != 0:
            if split_step(err_est, 4, eps) == 2:  # Второй случай
                h *= 2
                # v_ic[i] = info['inc'] = info['inc']+1
                info['inc'] = info['inc'] + 1

        vy[i] = y = y + (k1 + k2 + k2 + k3 + k3 + k4) / 6
        # vy[i] = y = w
        table['W-V'][i] = (w - y)
        vw[i] = w
        vh[i] = h
        v_ic[i] = info['inc']
        v_dc[i] = info['deg']
        i += 1
        if (x > x1 - eps_bord) and (x <= x1):
            break

    info['n'] = i
    # Удаление "лишнего хвоста"
    for j in range(max_n - i + 1):
        vx.pop()
        vy.pop()
        vh.pop()
        vw.pop()
        vs.pop()
        v_ic.pop()
        v_dc.pop()
        table['W-V'].pop()
    table['X'] = vx
    table['Y'] = vy
    table['H'] = vh
    table['W'] = vw
    table['S'] = vs
    table['local'] = vs*16
    table['inc_count'] = v_ic
    table['deg_count'] = v_dc
    # return vx, vy, info
    return table, info

# SYSTEM

def error_estimation_func_for_system(w1, w2, y1, y2, p):
    tmp1 = w1 - y1
    tmp2 = w2 - y2
    if abs(tmp1) > abs(tmp2):
        return abs(tmp1) /(-1 + 2 ** p)
    else:
        return abs(tmp2) / (2 ** p - 1)


def calc_coeff_for_system(f1, f2, x, y1, y2, h, param_a):
    q = [[0.] * 4] * 2
    res = np.array(q, dtype=np.float64)
    res[0][0] = h * f1(x, y1, y2, param_a)
    res[1][0] = h * f2(x, y1, y2, param_a)

    res[0][1] = h * f1(x + 0.5 * h, y1 + 0.5 * res[0][0], y2 + 0.5 * res[1][0], param_a)
    res[1][1] = h * f2(x + 0.5 * h, y1 + 0.5 * res[0][0], y2 + 0.5 * res[1][0], param_a)

    res[0][2] = h * f1(x + 0.5 * h, y1 + 0.5 * res[0][1], y2 + 0.5 * res[1][1], param_a)
    res[1][2] = h * f2(x + 0.5 * h, y1 + 0.5 * res[0][1], y2 + 0.5 * res[1][1], param_a)

    res[0][3] = h * f1(x + h, y1 + res[0][2], y2 + res[1][2], param_a)
    res[1][3] = h * f2(x + h, y1 + res[0][2], y2 + res[1][2], param_a)
    return res


def double_calc_for_system(f1, f2, x, y1, y2, h, param_a):
    tmp_x = x + h / 2
    K = calc_coeff_for_system(f1, f2, x, y1, y2, h / 2, param_a)
    tmp_y1 = y1 + (K[0][0] + 2 * K[0][1] + 2 * K[0][2] + K[0][3]) / 6
    tmp_y2 = y2 + (K[1][0] + 2 * K[1][1] + 2 * K[1][2] + K[1][3]) / 6
    K = calc_coeff_for_system(f1, f2, tmp_x, tmp_y1, tmp_y2, h / 2, param_a)
    tmp_y1 = tmp_y1 + (K[0][0] + 2 * K[0][1] + 2 * K[0][2] + K[0][3]) / 6
    tmp_y2 = tmp_y2 + (K[1][0] + 2 * K[1][1] + 2 * K[1][2] + K[1][3]) / 6
    return tmp_y1, tmp_y2


def rk4_for_system(f1, f2, x0, y10, y20, x1, h, max_n, param_a, eps_bord, flag_inc_step, flag_deg_step, eps):
    info = dict.fromkeys(
        ['n', 'inc', 'deg', 'max err est', 'X	on max err est', 'min err est', 'X on min err est', 'x1', 'eps',
         'eps_bord', 'a'])  # err est - оценка погрешности
    table = dict.fromkeys(
        ['X', 'Y1', 'Y2', 'H', 'W1', 'W2', 'W-V', 'S', 'inc_count', 'deg_count', 'local'])  # См. Методичу страница 13
    info['n'] = 0
    info['inc'] = 0
    info['deg'] = 0
    info['max err est'] = np.float64(0)
    info['min err est'] = np.float64(999)
    info['x1'] = x1
    info['eps'] = eps
    info['eps_bord'] = eps_bord
    info['a'] = param_a
    # Выделение памяти

    table['W-V'] = [0] * (max_n + 1)
    vx = [0] * (max_n + 1)  # Значение	x для каждого шага
    vy1 = [0] * (max_n + 1)  # Значение	y1 для каждого шага
    vy2 = [0] * (max_n + 1)  # Значение y2 для каждого шага
    vh = [0] * (max_n + 1)  # Значение	h для каждого шага
    vw1 = [0] * (max_n + 1)  # Значение	w для каждого шага
    vw2 = [0] * (max_n + 1)  # Значение	w для каждого шага
    v_ic = [0] * (max_n + 1)  # Значение inc_count	для	каждого	шага
    v_dc = [0] * (max_n + 1)  # Значение deg_count	для	каждого	шага
    vs = [0] * (max_n + 1)  # Значение	s для каждого шага
    vx[0] = x = x0
    vy1[0] = y1 = y10
    vy2[0] = y2 = y20
    i = 1
    vh[0] = h
    while (i) < max_n:
        v_ic[i] = info['inc']
        v_dc[i] = info['deg']
        #	Проверка выхода	за границу
        if x + h > x1:
            h = h / 2
            v_dc[i] = info['deg'] = info['deg'] + 1
            continue
        K = calc_coeff_for_system(f1, f2, x, y1, y2, h, param_a)  # Подсчет коэффициентов для метода РК*
        w1, w2 = double_calc_for_system(f1, f2, x, y1, y2, h, param_a)
        vx[i] = x = x + h
        vs[i] = err_est = error_estimation_func_for_system(w1, w2,
                                                           y1 + (K[0][0] + 2 * K[0][1] + 2 * K[0][2] + K[0][3]) / 6,
                                                           y2 + (K[1][0] + 2 * K[1][1] + 2 * K[1][2] + K[1][3]) / 6, 4)

        #	Выбор максимальной и минимальной оценки	погрешности

        if abs(info['max err est']) < abs(err_est):
            info['max err est'] = abs(err_est)
            info['X on max err est'] = x
        if abs(info['min err est']) > abs(err_est):
            info['min err est'] = abs(err_est)  # Добавить условие чтобы	сюда не	ставил ошибку из начальной точки
            info['X on min err est'] = x  # Подсчет следующей точки с двойной точностью

        #	Изменение шага
        if flag_deg_step != 0:
            if (split_step(err_est, 4, eps) == 3):  # Третий	случай
                x = x - h
                h /= 2
                # v_dc[i] =	info['deg']	= info['deg']+1
                info['deg'] = info['deg'] + 1
                continue  # Прераваем текущую итерацию цикла т.е. не увидичиваем i уменьшаем шаг
        if flag_inc_step != 0:
            if split_step(err_est, 4, eps) == 2:  # Второй случай
                h *= 2
                # v_ic[i] =	info['inc']	= info['inc']+1
                info['inc'] = info['inc'] + 1

        vy1[i] = y1 = y1 + (K[0][0] + 2 * K[0][1] + 2 * K[0][2] + K[0][3]) / 6
        vy2[i] = y2 = y2 + (K[1][0] + K[1][1] + K[1][1] + K[1][2] + K[1][2] + K[1][3]) / 6
        #	vy[i] =	y =	w
        if abs(w1 - y1) > abs(w2 - y2):
            table['W-V'][i] = abs(w1 - y1)
        else:
            table['W-V'][i] = abs(w2 - y2)
        vw1[i] = w1
        vw2[i] = w2
        vh[i] = h
        v_ic[i] = info['inc']
        v_dc[i] = info['deg']
        i += 1
        if (x > x1 - eps_bord) and (x <= x1):
            break

    info['n'] = i
    # Удаление	"лишнего хвоста"
    for j in range(max_n - i + 1):
        vx.pop()
        vy1.pop()
        vy2.pop()
        vh.pop()
        vw1.pop()
        vw2.pop()
        vs.pop()
        v_ic.pop()
        v_dc.pop()
        table['W-V'].pop()
    table['X'] = vx
    table['Y1'] = vy1
    table['Y2'] = vy2
    table['H'] = vh
    table['W1'] = vw1
    table['W2'] = vw2
    table['S'] = vs
    table['local'] = vs * 16
    table['inc_count'] = v_ic
    table['deg_count'] = v_dc
    # return vx, vy, info
    return table, info
